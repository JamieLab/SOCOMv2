#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 27/04/2026

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
working_loc = 'D:/OSSE_Experiments'

run_full = True
run_sampled = False
if run_full:
    models = [os.path.join(working_loc,'truth','FESOM2_REcoM'),
            os.path.join(working_loc,'truth','IPSL_NEMO_PISCES'),
            os.path.join(working_loc,'truth','MRI_ESM2'),
            os.path.join(working_loc,'truth','CESM'),
            os.path.join(working_loc,'truth','Princeton')
            ]

    ref_yr = 1980
    ref_mon = 1
    end_yr = 2024
    for model in models:
        g = glob.glob(os.path.join(model,'*'+str(ref_yr)+'_'+str(end_yr)+'.nc'))
        print(g)
        for i in range(len(g)):
            a = g[i].split('\\') # Here we split out the name of the file from the rest of the file path
            a = a[-1].split('_') # Here we split the file name by underscores to get the variable name of the variable within
            print(a)
            #Make the folder the individual data will go into
            du.makefolder(os.path.join(model,a[0]))
            if a[0] == 'xco2':
                c = Dataset(g[i],'r')
                data = np.array(c[a[0]])
                lon,lat = du.reg_grid()
                yr = ref_yr
                mon = ref_mon
                ti = 0
                while ti < sh[0]:
                    file = os.path.join(model,a[0],str(yr)+'_'+du.numstr(mon)+'_'+a[0]+'.nc')
                    temp_data = np.zeros((360,180))
                    temp_data[:] = data[ti]

                    du.netcdf_create_basic(file,temp_data,a[0],lat,lon)

                    mon = mon+1
                    if mon == 13:
                        mon = 1
                        yr=yr+1
                    ti = ti+1

            else:

                c = Dataset(g[i],'r')
                data = np.array(c[a[0]])
                lat = np.array(c['lat'])
                lon = np.array(c['lon'])-180
                try:
                    data[data == c[a[0]]._FillValue] = np.nan
                except:
                    print('No fill value')
                c.close()

                if a[0] == 'mld':
                    data = np.log10(data)
                if a[0] == 'chl':
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
if run_sampled:
    c = Dataset(os.path.join(working_loc,'common_mask_for_models.nc'),'r')
    mask = np.roll(np.transpose(np.array(c['all_model_mask'])),180,axis=0)
    c.close()

    models = [os.path.join(working_loc,'truth','IPSL_NEMO_PISCES'),
            os.path.join(working_loc,'truth','MRI_ESM2')]
    ref_yr = 1980
    ref_mon = 1
    end_yr = 2024
    for model in models:
        g = glob.glob(os.path.join(model,'*'+str(ref_yr)+'_'+str(end_yr)+'.nc'))
        print(g)
        for i in range(len(g)):
            a = g[i].split('\\') # Here we split out the name of the file from the rest of the file path
            a = a[-1].split('_') # Here we split the file name by underscores to get the variable name of the variable within
            print(a)
            #Make the folder the individual data will go into
            du.makefolder(os.path.join(model,a[0]+'_masked'))
            if a[0] == 'xco2':
                c = Dataset(g[i],'r')
                data = np.array(c[a[0]])
                lon,lat = du.reg_grid()
                yr = ref_yr
                mon = ref_mon
                ti = 0
                while ti < sh[0]:
                    file = os.path.join(model,a[0]+'_masked',str(yr)+'_'+du.numstr(mon)+'_'+a[0]+'.nc')
                    temp_data = np.zeros((360,180))
                    temp_data[:] = data[ti]
                    temp_data[mask==0] = np.nan
                    du.netcdf_create_basic(file,temp_data,a[0],lat,lon)

                    mon = mon+1
                    if mon == 13:
                        mon = 1
                        yr=yr+1
                    ti = ti+1

            else:

                c = Dataset(g[i],'r')
                data = np.array(c[a[0]])
                lat = np.array(c['lat'])
                lon = np.array(c['lon'])-180
                try:
                    data[data == c[a[0]]._FillValue] = np.nan
                except:
                    print('No fill value')
                c.close()

                if a[0] == 'mld':
                    data = np.log10(data)
                if a[0] == 'chl':
                    data = np.log10(data)

                if a[0] == 'fice': # Small precision error bug in NorESM leads to fice being negative at the 8th decimal place (-0.00000004) causing issues in the flux.
                    data[data<0] = 0.0
                sh = data.shape
                yr = ref_yr
                mon = ref_mon
                ti = 0
                while ti < sh[0]:
                    file = os.path.join(model,a[0]+'_masked',str(yr)+'_'+du.numstr(mon)+'_'+a[0]+'.nc')
                    temp_data = data[ti,:,:]
                    temp_data = du.lon_switch_2d(temp_data)
                    temp_data = temp_data.transpose()
                    temp_data[mask==0] = np.nan
                    du.netcdf_create_basic(file,temp_data,a[0],lat,lon)

                    mon = mon+1
                    if mon == 13:
                        mon = 1
                        yr=yr+1
                    ti = ti+1
