#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 17/01/2025

"""
cols = ['#332288','#44AA99','#882255', '#117733', '#88CCEE','#999933','#CC6677','#AA4499'] # '#DDCC77' IPSL colour

import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats
oceanicu_loc = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(oceanicu_loc)
sys.path.append(os.path.join(oceanicu_loc,'Data_Loading'))
import data_utils as du
import fluxengine_driver as fl

def lon_switch(var):
    temp = np.zeros((var.shape))
    temp[:,:,0:180] = var[:,:,180:]
    temp[:,:,180:] = var[:,:,0:180]
    return temp

def lon_switch_2d(var):
    temp = np.zeros((var.shape))
    temp[:,0:180] = var[:,180:]
    temp[:,180:] = var[:,0:180]
    return temp
# Setting up so we can retrieve the right model (tos,sos, etc) for the data product...
input_location = 'E:/SOCOMV2/EX2'
flux_location = 'E:/SOCOMV2/EX2/flux/'
model_location = os.path.join(flux_location,'models')
data_prod_location = os.path.join(flux_location,'data_products')
bath_file=os.path.join(flux_location,'bath.nc')
c = Dataset(bath_file,'r')
mask_sfc = np.array(c['ocean_proportion'])
c.close()



data_folds = []
obj = os.scandir(data_prod_location)
for entry in obj:
    if entry.is_dir():
        data_folds.append(entry.name)
print(data_folds)
mod_dictionary = {'FESOM': 'FESOM2_REcoM',
    'CESM': 'CESM_ETHZ_r1',
    #'IPSL': 'IPSL_r1', # IPSL does not have the fields required.
    'MRI': 'MRI_ESM2_2',
    'NorESM': 'NorESM_vGCB2024'}
mod_keys = list(mod_dictionary.keys())
print(mod_keys)

kw_names = ['Kw','kw','Kw660']

for i in mod_keys:
    g = glob.glob(os.path.join(input_location,'Input-from-ocean-models',mod_dictionary[i],'Kw_*.nc'))
    print(g)
    c = Dataset(g[0],'r')
    t = 'time'
    try:
        time = np.array(c[t])
    except:
        print('Not ' + t)
        t = 'Time'
    try:
        time = np.array(c[t])
    except:
        print('Not '+ t)
    # Assuming they are all starting in 1959...
    yr = 1959; mon=1
    times = []
    for j in range(len(time)):
        times.append(yr)
        mon = mon+1
        if mon == 13:
            yr = yr+1
            mon=1
    times = np.array(times)
    time_cut = np.where((times >= 1970) & (times <= 2022))
    for k in kw_names:
        try:
            kw = np.array(c[k])
            kw_name = k
            break;
        except:
            print('Not ' + k)
    kw[kw>1000] = np.nan
    print(kw_name)
    kw = kw*360000
    kw = kw[time_cut,:,:]
    #print(kw)
    c.close()

    c = Dataset(os.path.join(flux_location,'final_output',mod_dictionary[i]+'_full_variables.nc'),'a')
    c.last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    schmidt = np.array(c['schmidt'])
    sol = np.array(c['solubility'])
    dfco2 = np.array(c['model_dfco2'])

    if (kw_name == 'Kw660'):
        kw = kw * np.sqrt(660.0/schmidt)

    ice = np.array(c['ice'])
    kw = kw / (1-ice)
    #print(kw)
    if 'model_gas_transfer' in c.variables.keys():
        c['model_gas_transfer'][:] = kw
    else:
        var = c.createVariable('model_gas_transfer','f4',('time','lat','lon'))
        var[:] = kw
    c['model_gas_transfer'].Long_name = 'Model Gas transfer coefficient at the Schmidt number'
    c['model_gas_transfer'].Units = 'cm hr-1'
    c['model_gas_transfer'].formulation = '(660/Schmidt)^-0.5 * kw'
    c['model_gas_transfer'].last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))

    concfactor = 12.011/1000 # mol l-1 -> g m-3
    kfactor = 24/100 # cmhr-1 -> m day-1

    flux = np.squeeze(kw * kfactor * ( concfactor * sol * dfco2) * (1-ice))
    if 'model_flux_model_gas_transfer' in c.variables.keys():
        c['model_flux_model_gas_transfer'][:] = flux
    else:
        var = c.createVariable('model_flux_model_gas_transfer','f4',('time','lat','lon'))
        var[:] = flux
    c['model_flux_model_gas_transfer'].Long_name = 'Model air-sea CO2 flux using model provided gas transfer'
    c['model_flux_model_gas_transfer'].Units = 'g C m-2 d-1'
    c['model_flux_model_gas_transfer'].last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    c.close()
    print(flux.shape)
    print(np.transpose(flux,(2,1,0)).shape)

    c = Dataset(os.path.join(model_location,mod_dictionary[i],'combined_variables.nc'),'a')
    if 'model_flux_model_gas_transfer_2' in c.variables.keys():
        c['model_flux_model_gas_transfer_2'][:] = np.transpose(lon_switch(flux),(2,1,0))
    else:
        var = c.createVariable('model_flux_model_gas_transfer_2','f4',('longitude','latitude','time'))
        var[:] = np.transpose(lon_switch(flux),(2,1,0))
    c['model_flux_model_gas_transfer_2'].Long_name = 'Model air-sea CO2 flux using model provided gas transfer'
    c['model_flux_model_gas_transfer_2'].Units = 'g C m-2 d-1'
    c['model_flux_model_gas_transfer_2'].last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    c.close()
    log,lag = du.reg_grid(lat=1,lon=1)
    start_yr = 1970
    end_yr = 2022
    output_loc = os.path.join(flux_location,'models')
    fl.calc_annual_flux(os.path.join(output_loc,mod_dictionary[i]),log,lag,start_yr,end_yr,bath_file=bath_file,flux_file = os.path.join(output_loc,mod_dictionary[i],'combined_variables.nc'),save_file = os.path.join(output_loc,mod_dictionary[i],mod_dictionary[i]+'_full_model_k.csv')
        ,flux_var='model_flux_model_gas_transfer_2')
    del kw
    del kw_name

import matplotlib.transforms
font = {'weight' : 'normal',
        'size'   :10}
matplotlib.rc('font', **font)
model_gcb = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/GCB_model_fluxes.csv'
data = pd.read_table(model_gcb,sep=','); head = list(data); head.remove('year'); head.remove('IPSL_r1')
plt.figure(figsize=(10,10))
co = 0
for t in head:
    stat = scipy.stats.linregress(data['year'],data[t])
    print(stat)
    plt.plot(data['year'],data[t],label=t+' (GCB2023) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$)',color=cols[co])
    model_f = os.path.join(model_location,t,t+'_full_model_k.csv')
    data2 = pd.read_table(model_f,sep=',')
    stat = scipy.stats.linregress(data2['# Year'],-data2['Net air-sea CO2 flux (Pg C yr-1)'])
    plt.plot(data2['# Year'],-data2['Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--',label=t+' (SOCOMv2) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$)')
    co = co+1

plt.ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
plt.xlabel('Year')
plt.title('SOCOMv2 Ex2 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
plt.ylim([0,4])
plt.grid()
plt.legend()
plt.savefig('plots/SOCOMv2_model_k_comparision_offlinevsonline.png',format='png',dpi=300)
