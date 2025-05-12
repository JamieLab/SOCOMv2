#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 06/2024

"""
cols = ['#332288','#44AA99','#882255','#DDCC77', '#117733', '#88CCEE','#999933','#CC6677','#AA4499']
import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.gridspec import GridSpec
from fluxengine.core import fe_setup_tools as fluxengine
import shutil
import scipy.stats

def lon_switch(var):
    temp = np.zeros((var.shape))
    temp[:,:,0:180] = var[:,:,180:]
    temp[:,:,180:] = var[:,:,0:180]
    return temp
# worldmap = gpd.read_file(gpd.datasets.get_path("ne_50m_land"))

#Location of OceanICU neural network framework
oceanicu = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(os.path.join(oceanicu,'Data_Loading'))
sys.path.append(oceanicu)
import data_utils as du
import construct_input_netcdf as cinp
import fluxengine_driver as fl

def load_sfco2(model_location):
    c = Dataset(os.path.join(model_location,'combined_variables.nc'),'r')
    lon = c['longitude'][:]
    lat = c['latitude'][:]
    sfco2 = c['model_sfco2'][:]
    c.close()

    return lon,lat,sfco2
import data_utils as du
#Locations of the model files...
#models = []
models = [
    'E:/SOCOMV2/EX2/flux/models/FESOM2_REcoM',
    'E:/SOCOMV2/EX2/flux/models/MRI_ESM2_2',
    'E:/SOCOMV2/EX2/flux/models/CESM_ETHZ_r1',
    'E:/SOCOMV2/EX2/flux/models/IPSL_r1',
    'E:/SOCOMV2/EX2/flux/models/NorESM_vGCB2024']
model_gcb = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/GCB_model_fluxes.csv'
a_scale = [0.251,0.251,0.310,0.251,0.337]

log,lag = du.reg_grid(lat=1,lon=1)
inp_loc = 'E:/SOCOMV2/EX2/flux'
model_loc = 'E:/SOCOMV2/EX2/flux/models'
output_loc = 'E:/SOCOMV2/EX2/flux/final_output'
add_final = True
for i in range(len(models)):
    flux_config = f'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/SOCOMv2_flux_config_a{a_scale[i]}.conf'
    data_file_o = os.path.join(models[i],'combined_variables.nc')
    data_file = os.path.join(models[i],f'combined_variables_{int(a_scale[i]*1000)}.nc')
    shutil.copyfile(data_file_o, data_file)
    start_yr = 1970
    end_yr = 2022
    if os.path.isdir(os.path.join(models[i],f'flux_a{int(a_scale[i]*1000)}')) == False:
        return_path = os.getcwd()
        os.chdir(models[i])
        returnCode, fe = fluxengine.run_fluxengine(flux_config, start_yr, end_yr, singleRun=False,verbose=True)
        os.chdir(return_path)
    print(os.path.join(models[i],f'flux_a{int(a_scale[i]*1000)}'))
    flux = fl.load_flux_var(os.path.join(models[i],f'flux_a{int(a_scale[i]*1000)}'),'OF',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
    ice = fl.load_flux_var(os.path.join(models[i],f'flux_a{int(a_scale[i]*1000)}'),'P1',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
    dpco2 = fl.load_flux_var(os.path.join(models[i],f'flux_a{int(a_scale[i]*1000)}'),'dpCO2',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
    k = fl.load_flux_var(os.path.join(models[i],f'flux_a{int(a_scale[i]*1000)}'),'OK3',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)

    flux = flux * (1-ice)
    flux = np.transpose(flux,(1,0,2))
    ice = np.transpose(ice,(1,0,2))
    dpco2 = np.transpose(dpco2,(1,0,2))
    k = np.transpose(k,(1,0,2))
    #
    c = Dataset(data_file,'a')
    keys = c.variables.keys()
    if 'flux' in keys:
        c.variables['flux'][:] = flux
    else:
        var_o = c.createVariable('flux','f4',('longitude','latitude','time'))
        var_o[:] = flux
    if 'ice' in keys:
        c.variables['ice'][:] = ice
    else:
        var_o = c.createVariable('ice','f4',('longitude','latitude','time'))
        var_o[:] = ice
    if 'dfCO2' in keys:
        c.variables['dfCO2'][:] = dpco2
    else:
        var_o = c.createVariable('dfCO2','f4',('longitude','latitude','time'))
        var_o[:] = dpco2
    c.close()
    m = models[i].split('/')
    fl.calc_annual_flux(models[i],log,lag,start_yr,end_yr,bath_file=os.path.join(inp_loc,'bath.nc'),flux_file = data_file,save_file = os.path.join(models[i],m[-1]+f'_full_a{int(a_scale[i]*1000)}.csv'))

    if add_final:
        print(flux.shape)
        print(np.transpose(flux,(2,1,0)).shape)
        c = Dataset(os.path.join(output_loc,models[i].split('/')[-1]+'_full_variables.nc'),'a')
        keys = c.variables.keys()
        if 'model_flux_model_estimated_gas_transfer' in keys:
            c.variables['model_flux_model_estimated_gas_transfer'][:] = lon_switch(np.transpose(flux,(2,1,0)))
        else:
            var_o = c.createVariable('model_flux_model_estimated_gas_transfer','f4',('time','lat','lon'))
            var_o[:] = lon_switch(np.transpose(flux,(2,1,0)))
            var_o.Long_name = "Model air-sea CO2 flux calculated with a model estimated gas transfer"
            var_o.Units = 'g C m-2 d-1'
            var_o.comment = 'Gas transfer estimated with ERA5 winds and a scaling of: '+str(a_scale[i])

        if 'model_estimated_gas_transfer' in keys:
            c.variables['model_estimated_gas_transfer'][:] = lon_switch(np.transpose(k,(2,1,0)))
        else:
            var_o = c.createVariable('model_estimated_gas_transfer','f4',('time','lat','lon'))
            var_o[:] = lon_switch(np.transpose(k,(2,1,0)))
        c.variables['model_estimated_gas_transfer'].Long_name = "Gas transfer coefficient at the Schmidt number estimated with model parameterisation"
        c.variables['model_estimated_gas_transfer'].Units = 'cm hr-1'
        c.variables['model_estimated_gas_transfer'].comment = 'Gas transfer estimated with ERA5 winds and a scaling of: '+str(a_scale[i])
        c.variables['model_estimated_gas_transfer'].last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
        c.variables['model_flux_model_estimated_gas_transfer'].last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
        c.close()

#### Plotting
# import matplotlib.transforms
# font = {'weight' : 'normal',
#         'size'   : 12}
# matplotlib.rc('font', **font)
# label = ['SOCOMv2 NorESM','GCB2024 NorESM']
# model_gcb = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/GCB_model_fluxes.csv'
# gcb_data = pd.read_table(model_gcb,sep=',')
# sfco2=[]
#
# for model in models:
#     lon,lat,sfco2_t = load_sfco2(model)
#     sfco2.append(sfco2_t)
#
# fig,ax = plt.subplots(1,figsize=(15,7))
# worldmap.plot(color="lightgrey", ax=ax,zorder=2)
# dif = np.nanmean(sfco2[0] - sfco2[1],axis=2)
# a = ax.pcolor(lon,lat,np.transpose(dif),zorder=1)
# c= plt.colorbar(a)
# c.set_label('NorESM_SOCOMv2 - NorESM_GCB2024 sfCO2 (mean 1970 to 2022)')
# fig.savefig('NorESM-GCB_SOCOMv2_compare.png',dpi=300)
#
#
#
#
import matplotlib.transforms
font = {'weight' : 'normal',
        'size'   :10}
matplotlib.rc('font', **font)
years_lims = [1970,2022]
data = pd.read_table(model_gcb,sep=',')

#print(data)
head = list(data); head.remove('year')
#print(head)

plt.figure(figsize=(10,10))
co = 0
for t in head:
    stat = scipy.stats.linregress(data['year'],data[t])
    print(stat)
    plt.plot(data['year'],data[t],label=t+' (GCB2023) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$)',color=cols[co])
    model_f = os.path.join(model_loc,t,t+f'_full_a{int(a_scale[co]*1000)}.csv')
    data2 = pd.read_table(model_f,sep=',')
    stat = scipy.stats.linregress(data2['# Year'],-data2['Net air-sea CO2 flux (Pg C yr-1)'])
    plt.plot(data2['# Year'],-data2['Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--',label=t+' (SOCOMv2) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$) - ' + f'a = {a_scale[co]}')
    co = co+1

plt.ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
plt.xlabel('Year')
plt.title('SOCOMv2 Ex2 Model a scaling - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
plt.ylim([0,4])
plt.grid()
plt.legend()
plt.savefig('plots/SOCOMv2_model_flux_comparision_model_a_scaling.png',format='png',dpi=300)
