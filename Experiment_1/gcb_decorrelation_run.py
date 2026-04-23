#!/usr/bin/env python3
import numpy as np
import datetime
from netCDF4 import Dataset
import numpy as np
import glob
import os
import sys
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
# import matplotlib.transforms
# font = {'weight' : 'normal',
#         'size'   : 15}
#
# matplotlib.rc('font', **font)
oceanicu_frame = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'

sys.path.append(os.path.join(oceanicu_frame))
sys.path.append(os.path.join(oceanicu_frame,'Data_Loading'))

import fluxengine_driver as fl
import data_utils as du
import Data_Loading.ESA_CCI_land as landcci

working_directory = 'D:/SOCOMv2/Experiment1/GCB2025'
start_yr = 1990
end_yr = 2024
input_file = os.path.join(working_directory,'output_GCBv2025.nc')
model_save_loc = working_directory
recalculated_socat_prod = ['UExP-FNN-U','JMA-MLR']
lon,lat = du.reg_grid()

du.make_folder(os.path.join(working_directory,'flux'))
du.make_folder(os.path.join(working_directory,'plots'))
du.make_folder(os.path.join(working_directory,'decorrelation'))

landcci.generate_land_cci('E:/Data/Land-CCI/ESACCI-LC-L4-WB-Map-150m-P13Y-2000-v4.0.nc','E:/Data/Land-CCI/ESACCI-LC-L4-WB-Ocean-Map-150m-P13Y-2000-v4.0.tif',lon,lat,os.path.join(working_directory,'inputs','bath.nc'))

c = Dataset(input_file,'r')
keys = list(c.variables.keys())
c.close()
matching = [s for s in keys if "sfco2" in s]


for v in matching:
    print(v)
    s = v.split('_')
    if not du.checkfileexist(os.path.join(working_directory,'decorrelation',s[0]+'.csv')):
        if any(p in v for p in recalculated_socat_prod):
            print('Recalculated product')
            fl.variogram_evaluation(model_save_loc,input_array = ['fco2_recalculated_ave_weighted',v],input_datafile=[input_file,input_file], start_yr=start_yr,end_yr=end_yr,output_file=s[0])
        else:
            print('Original product')
            fl.variogram_evaluation(model_save_loc,input_array = ['fco2_ave_weighted',v],input_datafile=[input_file,input_file], start_yr=start_yr,end_yr=end_yr,output_file=s[0])

    if not du.checkfileexist(os.path.join(working_directory,'flux',s[0]+'_flux.csv')):
        fl.calc_annual_flux(model_save_loc,
            lon=lon,
            lat=lat,
            start_yr=start_yr,
            end_yr=end_yr,
            flux_file = input_file,
            flux_var = s[0]+'_fgco2',
            save_file = os.path.join(working_directory,'flux',s[0]+'_flux.csv'))

    if not du.checkfileexist(os.path.join(working_directory,s[0]+'.csv')):
        fl.montecarlo_flux_testing(model_save_loc=model_save_loc,
            start_yr = start_yr,
            end_yr = end_yr,
            decor=os.path.join(working_directory,'decorrelation',s[0]+'.csv'),
            flux_var = s[0]+'_unc',
            flux_variable = s[0]+'_fgco2',
            inp_file = input_file,
            single_output = os.path.join(working_directory,s[0]),
            ens=100)
