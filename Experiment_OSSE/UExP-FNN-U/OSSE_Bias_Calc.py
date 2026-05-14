import os
import sys
import datetime
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
oceanicu_framework = 'C:\\Users\\df391\\OneDrive - University of Exeter\\Post_Doc_ESA_Contract\\OceanICU'


sys.path.append(os.path.join(oceanicu_framework,'Data_Loading'))
sys.path.append(os.path.join(oceanicu_framework))
import data_utils as du
working_dir = 'D:/OSSE_Experiments/UExP-FNN-U'

# locs = [os.path.join(working_dir,'Base_FESOM2_REcoM'),
        # os.path.join(working_dir,'Base+ALL_FESOM2_REcoM'),
        # os.path.join(working_dir,'Base_IPSL_NEMO_PISCES'),
        # os.path.join(working_dir,'Base+ALL_IPSL_NEMO_PISCES'),
locs = [os.path.join(working_dir,'Base_MRI_ESM2'),
        os.path.join(working_dir,'Base+ALL_MRI_ESM2'),
        os.path.join(working_dir,'Base+Disc_MRI_ESM2'),
        # os.path.join(working_dir,'Base+RV_MRI_ESM2'),
        os.path.join(working_dir,'Base+VOS_MRI_ESM2')]

row = 2
col = 2

fig,ax = plt.subplots(row,col,figsize=(row*4,col*4))
ax = ax.ravel()
start_yr = 1980
end_yr=2024
for i in range(len(locs)):
    c = Dataset(os.path.join(locs[i],'output.nc'))
    fco2 = np.array(c.variables['fco2'])
    c.close()

    c = Dataset(os.path.join(locs[i],'inputs','bath.nc'))
    area = np.array(c.variables['area']) * np.array(c.variables['ocean_proportion'])
    c.close()

    c = Dataset(os.path.join(locs[i],'inputs','neural_network_input.nc'))
    full = np.array(c.variables['model_full_sfco2'])
    c.close()

    area = np.repeat(area[:, :, np.newaxis], fco2.shape[2], axis=2)

    bias = fco2 - full

    yr = start_yr

    ann_bias = []
    j = 0
    while yr <= end_yr:
        temp = bias[:,:,j:j+12]
        temp_area = area[:,:,j:j+12]
        f = np.where(np.isnan(temp) == 0)
        temp = temp[f]
        temp_area = temp_area[f]

        ann_bias.append(np.average(temp,weights=temp_area))
        # print(ann_bias)
        j = j+12
        yr = yr+1

    ax[0].plot(np.arange(1980,2025),ann_bias,label = locs[i].split('\\')[1])

ax[0].legend(fontsize=7)
plt.show()
