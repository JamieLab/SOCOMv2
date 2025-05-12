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
from fluxengine.core import fe_setup_tools as fluxengine
import pandas as pd
#Setting up OceanICU framework to use within the work...
oceanicu_loc = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(oceanicu_loc)
sys.path.append(os.path.join(oceanicu_loc,'Data_Loading'))
import data_utils as du
import construct_input_netcdf as cinp
import fluxengine_driver as fl

def lon_switch(var):
    temp = np.zeros((var.shape))
    temp[:,:,0:180] = var[:,:,180:]
    temp[:,:,180:] = var[:,:,0:180]
    return temp

mod_dictionary = {'FESOM': 'FESOM2_REcoM',
    'CESM': 'CESM_ETHZ_r1',
    'IPSL': 'IPSL_r1',
    'MRI': 'MRI_ESM2_2',
    'NorESM': 'NorESM_vGCB2024'}
mod_keys = list(mod_dictionary.keys())
start_yr = 1985
end_yr=2022
inp_loc = 'E:/SOCOMV2/EX2/flux'
output_loc = os.path.join(inp_loc,'data_products')
model_loc = os.path.join(inp_loc,'models')
final_output = os.path.join(inp_loc,'final_output')
model_location = 'E:/SOCOMV2/EX2/Input-from-ocean-models'

g = glob.glob(os.path.join(final_output,'*.nc'))
print(g)

for i in g:
    c = Dataset(i,'a')
    c.last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    keys = c.variables.keys()
    p = []
    for t in keys:
        if 'flux' in t:
            p.append(t)

    for t in range(len(p)):
        t_flux = np.array(c.variables[p[t]])
        if t == 0:
            flux = np.zeros((t_flux.shape[0],t_flux.shape[1],t_flux.shape[2],len(p))); flux[:] = np.nan
        #t_flux[t_flux>800] = np.nan; t_flux[t_flux<-800] = np.nan;
        flux[:,:,:,t] = t_flux

    a = np.sum(np.isnan(flux),axis=3)
    mask = np.zeros((t_flux.shape))
    mask[a == 0] = 1

    if 'consistent_mask' in keys:
        c.variables['consistent_mask'][:] = mask
    else:
        var_o = c.createVariable('consistent_mask','f4',('time','lat','lon'))
        var_o[:] = mask
    c.variables['consistent_mask'].Long_name = 'Consistent grid mask'
    c.variables['consistent_mask'].comment = '1 indicates pixels that all data products cover'
    time = np.array(c.variables['time'])
    lat = np.array(c.variables['lat'])
    lon = np.array(c.variables['lon'])-180
    c.close()

    du.makefolder(os.path.join(final_output,'masks'))
    direct = {}
    direct['mask'] = np.transpose(lon_switch(mask),(2,1,0))
    cinp.save_netcdf(os.path.join(final_output,'masks',os.path.split(i)[-1]),direct,lon,lat,len(time),time_track=time)


g = glob.glob(os.path.join(output_loc,'*.nc'))

print(g)
log,lag = du.reg_grid(lat=1,lon=1) # Regular 1 deg grid (90N to 90S, -180W to 180W). All the additional flux data and model data are already
for prod in g:
    ## Here we check which model the data product output it for. (i.e which model data was used to produce it...)
    for i in mod_keys:
        if i in prod:
            model_ref = i
            break;
    print(model_ref)
    #Here we split the product filename so we can extract important info...
    a = prod.split('_')
    print(a)
    #start_yr = int(a[-1].split('-')[0])
    end_yr = 2022#int(a[-1][0:4]) # So we remove the .nc part of the final split component.
    product_name = a[-2] # This the the data product groups name...
    print(start_yr)
    print(end_yr)
    print(product_name)

    #Here we setup the flux calcualtion folder for the particular data product netcdf.
    #We name the folder, data product name and the model it's intended for.
    temp_out_loc = os.path.join(output_loc,product_name+'_'+model_ref)
    data_file = os.path.join(temp_out_loc,product_name+'_'+model_ref+'.nc')

    fl.calc_annual_flux(temp_out_loc,log,lag,start_yr,end_yr,bath_file=os.path.join(inp_loc,'bath.nc'),flux_file = data_file,save_file = os.path.join(temp_out_loc,product_name+'_'+model_ref+'_consistent.csv'),
        mask_file=os.path.join(final_output,'masks',mod_dictionary[model_ref]+'_full_variables.nc'))

g = glob.glob(os.path.join(model_location,'*'))
print(g)
models = []
for i in g:
    models.append(i.split('\\')[-1])
print(models)
# models.remove('NorESM_vGCB2024')
for mod in models:
    data_file = os.path.join(model_loc,mod,'combined_variables.nc')
    fl.calc_annual_flux(os.path.join(model_loc,mod),log,lag,start_yr,end_yr,bath_file=os.path.join(inp_loc,'bath.nc'),flux_file = data_file,save_file = os.path.join(model_loc,mod,mod+'_consistent.csv'),
        mask_file=os.path.join(final_output,'masks',mod+'_full_variables.nc'))


data_folds = []
obj = os.scandir(output_loc)
for entry in obj:
    if entry.is_dir():
        data_folds.append(entry.name)
print(data_folds)
#Generate basic csv file with intergrated ocean sink estimates
for i in mod_keys:
    #Load the model_flux file
    model_data = pd.read_table(os.path.join(model_loc,mod_dictionary[i],mod_dictionary[i]+'_consistent.csv'),delimiter=',')
    ke = model_data.keys()
    print(ke)
    # model_data = np.array(model_data)
    final_output = pd.DataFrame()
    final_output[ke[0]] = model_data[ke[0]]
    final_output['Model_Net_AirSea_Flux (PgCyr-1)'] = model_data[ke[1]]
    final_output['Model_Global_Area_Flux (m-2)'] = model_data[ke[4]]
    final_output['Model_Global_IceFree_Area_Flux (m-2)'] = model_data[ke[5]]
    mod_year = np.array(final_output[ke[0]])
    for j in data_folds:
        if i in j:
            print(j)
            pro = j.split('_')
            print(i)
            file = glob.glob(os.path.join(output_loc,j,'*'+'consistent.csv'))[0]
            prod_data = pd.read_table(file,delimiter=',')
            print(prod_data)
            year = np.array(prod_data['# Year'])
            net_flux = np.array(prod_data[ke[1]])
            area = np.array(prod_data[ke[4]])
            ice_free_area = np.array(prod_data[ke[5]])
            f = np.where(year[0] == mod_year)[0][0]
            print(f)
            net = np.zeros((len(mod_year))); net[:] = np.nan; net[f:] = net_flux
            ar = np.copy(net); ar[f:] = area
            ice_ar = np.copy(net); ice_ar[f:] = ice_free_area
            final_output[pro[0]+'_Net_AirSea_Flux (PgCyr-1)'] = net
            final_output[pro[0]+'_Global_Area_Flux (m-2)'] = ar
            final_output[pro[0]+'_Global_IceFree_Area_Flux (m-2)'] = ice_ar

    final_output.to_csv(os.path.join(inp_loc,'final_output',i+'_consistent.csv'),sep=',',index=False)
