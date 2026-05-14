import os
import sys
import datetime
import numpy as np
from netCDF4 import Dataset
oceanicu_framework = 'C:\\Users\\df391\\OneDrive - University of Exeter\\Post_Doc_ESA_Contract\\OceanICU'


sys.path.append(os.path.join(oceanicu_framework,'Data_Loading'))
sys.path.append(os.path.join(oceanicu_framework))
import data_utils as du

working_loc = 'D:/OSSE_Experiments'
version = 'v1'
log,lag = du.reg_grid(lat=1,lon=1)



import Data_Loading.ESA_CCI_land as landcci
# landcci.generate_land_cci('E:/Data/Land-CCI/ESACCI-LC-L4-WB-Map-150m-P13Y-2000-v4.0.nc','E:/Data/Land-CCI/ESACCI-LC-L4-WB-Ocean-Map-150m-P13Y-2000-v4.0.tif',log,lag,os.path.join(working_loc,'OSSE_ocean_area_mask_-180_180_'+version+'.nc'))

c = Dataset(os.path.join(working_loc,'OSSE_ocean_area_mask_-180_180_'+version+'.nc'),'a')
vars = ['ocean_proportion','area','land_proportion']
direct = {}
for i in vars:
    temp = np.array(c[i])
    temp = np.roll(temp,180,axis=0)
    direct[i] = temp

log = log+180
t =0
for i in list(direct.keys()):
    if t == 0:
        du.netcdf_create_basic(os.path.join(working_loc,'OSSE_ocean_area_mask_0_360_'+version+'.nc'),direct[i],i,lag,log,flip=True)
        t=1
    else:
        du.netcdf_append_basic(os.path.join(working_loc,'OSSE_ocean_area_mask_0_360_'+version+'.nc'),direct[i],i)

c = Dataset(os.path.join(working_loc,'OSSE_ocean_area_mask_0_360_'+version+'.nc'),'a')
c['area'].units = 'km2'
c['area'].generated_from = 'Assuming the Earth is an ellipsoid'
c['ocean_proportion'].generated_from = 'E:/Data/Land-CCI/ESACCI-LC-L4-WB-Map-150m-P13Y-2000-v4.0.nc and E:/Data/Land-CCI/ESACCI-LC-L4-WB-Ocean-Map-150m-P13Y-2000-v4.0.tif'
c['land_proportion'].generated_from = 'E:/Data/Land-CCI/ESACCI-LC-L4-WB-Map-150m-P13Y-2000-v4.0.nc and E:/Data/Land-CCI/ESACCI-LC-L4-WB-Ocean-Map-150m-P13Y-2000-v4.0.tif'
c.close()
