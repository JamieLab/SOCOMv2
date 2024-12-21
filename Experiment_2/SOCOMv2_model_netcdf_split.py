#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 06/2024

"""
import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys
import pandas as pd

#Location of OceanICU neural network framework
oceanicu = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(os.path.join(oceanicu,'Data_Loading'))
sys.path.append(oceanicu)

import data_utils as du
#Locations of the model files...
#models = []
models = ['E:/SOCOMV2/EX2/Input-from-ocean-models/CESM_ETHZ_r1',
    'E:/SOCOMV2/EX2/Input-from-ocean-models/FESOM2_REcoM',
    'E:/SOCOMV2/EX2/Input-from-ocean-models/IPSL_r1',
    'E:/SOCOMV2/EX2/Input-from-ocean-models/MRI_ESM2_2',
    'E:/SOCOMV2/EX2/Input-from-ocean-models/NorESM_vGCB2024']
ref_yr = 1970
ref_mon = 1
end_yr = 2022
for model in models:
    g = glob.glob(os.path.join(model,'*1970_2022.nc'))
    print(g)
    for i in range(len(g)):
        a = g[i].split('\\') # Here we split out the name of the file from the rest of the file path
        a = a[1].split('_') # Here we split the file name by underscores to get the variable name of the variable within
        print(a)
        du.makefolder(os.path.join(model,a[0])) #Make the folder the individual data will go into

        c = Dataset(g[i],'r')
        data = np.array(c[a[0]])
        lat = np.array(c['lat'])
        lon = np.array(c['lon'])-180

        c.close()

        if a[0] == 'mld':
            data = np.log10(data)
        if a[0] == 'fice': # Small precision error bug in NorESM leads to fice being negative at the 8th decimal place (-0.00000004) causing issues in the flux.
            data[data<0] = 0.0
        sh = data.shape
        yr = ref_yr
        mon = ref_mon
        ti = 0
        while ti < sh[0]:
            file = os.path.join(model,a[0],str(yr)+'_'+du.numstr(mon)+'_'+a[0]+'.nc')
            temp_data = data[ti,:,:]
            temp_data = du.lon_switch_2d(temp_data)
            temp_data = temp_data.transpose()
            du.netcdf_create_basic(file,temp_data,a[0],lat,lon)

            mon = mon+1
            if mon == 13:
                mon = 1
                yr=yr+1
            ti = ti+1

### Sorting the atmospheric component...

# xco2_atm_file = 'E:/SOCOMV2/EX2/Input-from-ocean-models/global_co2_merged.txt'
# atm_data = pd.read_table(xco2_atm_file,skiprows=16,delimiter=' ')
# print(atm_data)
# print(atm_data.keys())
# atm = np.array(atm_data['276.58'])
# time = np.array(atm_data['1700.042'])
# time_li = []
# for t in time:
#     l = (t - np.floor(t))*365
#     l = datetime.datetime(int(np.floor(t)),1,1) + datetime.timedelta(days=int(l))
#     time_li.append([l.year,l.month,l.day])
# time_li = np.array(time_li)
# lon,lat = du.reg_grid()
# for model in models:
#     m = model.split('/')
#     # if ('CESM' in m[-1]) or ('MRI_ESM' in model):
#     #     if 'CESM' in m[-1]:
#     #         file = glob.glob(os.path.join(model,'Ancil*.nc'))
#     #     else:
#     #         file = glob.glob(os.path.join(model,'Atm_CO2*.nc'))
#     #     print(file)
#     #     c = Dataset(file[0],'r')
#     #     time = np.array(c['time'])
#     #     atm = np.array(c['Atm_CO2'])
#     #     c.close()
#     #     time_li = []
#     #     for t in time:
#     #         temp_time = datetime.datetime(1959,1,1)+datetime.timedelta(days=int(t))
#     #         time_li.append([temp_time.year,temp_time.month,temp_time.day])
#     #     time_li = np.array(time_li)
#     #     print(time_li)
#     #
#     # if 'IPSL' in m[-1]:
#     #     file = glob.glob(os.path.join(model,'*ANC*.nc'))
#     #     print(file)
#     #     c = Dataset(file[0],'r')
#     #     time = np.array(c['TAXIS'])
#     #     atm_t = np.array(c['ATM_CO2'])
#     #     c.close()
#     #     yr = int(time[0])
#     #     mon= 1
#     #     time_li = []
#     #     atm = []
#     #     while yr<=end_yr:
#     #         time_li.append([yr,mon])
#     #         f = np.where(time == yr)[0]
#     #         atm.append(atm_t[f])
#     #         mon = mon+1
#     #         if mon==13:
#     #             yr = yr+1
#     #             mon=1
#     #     time_li = np.array(time_li)
#     #     atm = np.array(atm)
#     #
#     # if 'FESOM' in m[-1]:
#     #     file = glob.glob(os.path.join(model,'*AtmCO2*.nc'))
#     #     print(file)
#     #     c = Dataset(file[0],'r')
#     #
#     #     yr = ref_yr
#     #     mon = 1
#     #     time_li = []
#     #     atm = []
#     #     while yr <= end_yr:
#     #         if mon == 1:
#     #             atm_t = np.array(c['AtmCO2_'+str(yr)])
#     #         time_li.append([int(yr),int(mon)])
#     #         atm.append(atm_t[mon-1])
#     #
#     #         mon=mon+1
#     #         if mon == 13:
#     #             yr = yr+1
#     #             mon=1
#     #     c.close()
#     #     atm = np.array(atm)
#     #     time_li = np.array(time_li)
# #
# #
# #
# #
#     du.makefolder(os.path.join(model,'xCO2'))
#     for t in range(len(time_li)):
#         if time_li[t,0] >= ref_yr:
#             file = os.path.join(model,'xCO2',str(time_li[t,0])+'_'+du.numstr(time_li[t,1])+'_xCO2.nc')
#             atm_grid = np.ones((len(lon),len(lat)))*atm[t]
#             du.netcdf_create_basic(file,atm_grid,'xCO2',lat,lon)
