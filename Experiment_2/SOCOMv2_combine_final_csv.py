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
oceanicu_loc = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(oceanicu_loc)
sys.path.append(os.path.join(oceanicu_loc,'Data_Loading'))
import data_utils as du

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
    'IPSL': 'IPSL_r1',
    'MRI': 'MRI_ESM2_2',
    'NorESM': 'NorESM_vGCB2024'}
mod_keys = list(mod_dictionary.keys())
print(mod_keys)

#Generate basic csv file with intergrated ocean sink estimates
for i in mod_keys:
    #Load the model_flux file
    model_data = pd.read_table(os.path.join(model_location,mod_dictionary[i],mod_dictionary[i]+'_full.csv'),delimiter=',')
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
            file = glob.glob(os.path.join(data_prod_location,j,'*'+i+'.csv'))[0]
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

    final_output.to_csv(os.path.join(flux_location,'final_output',i+'_full.csv'),sep=',',index=False)

# Generate netcdf output of all the data for each model...
for i in mod_keys:

    #Load the model_data_file

    c = Dataset(os.path.join(model_location,mod_dictionary[i],'combined_variables.nc'),'r')
    lat = np.array(c['latitude'])
    lon = np.array(c['longitude'])
    time = np.array(c['time'])
    uni = c['time'].units
    #c.close()

    out = Dataset(os.path.join(flux_location,'final_output',mod_dictionary[i]+'_full_variables.nc'),'w')
    out.time_created = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    out.last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    out.generated_by = 'Daniel J. Ford (d.ford@exeter.ac.uk)'
    out.generated_from = flux_location

    out.createDimension('lon',lon.shape[0])
    out.createDimension('lat',lat.shape[0])
    out.createDimension('time',time.shape[0])

    var = out.createVariable('lat','f4',('lat'))
    var[:] = lat
    var.Long_name = 'Latitude'
    var.Units = 'Degrees North'

    var = out.createVariable('lon','f4',('lon'))
    var[:] = lon + 180 #Convert form -180 to 180, 0 to 360
    var.Long_name = 'Longitude'
    var.Units = 'Degrees East'

    var = out.createVariable('time','f4',('time'))
    var[:] = time
    var.Long_name = 'Time of observation'
    var.Units = uni

    var = out.createVariable('ice','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['ice']),[2,1,0]))
    var.Long_name = 'Ice coverage'
    var.dataset = 'Model ice'

    var = out.createVariable('wind','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['ERA5_ws']),[2,1,0]))
    var.Long_name = 'Wind speed'
    var.Units = 'ms-1'
    var.dataset = 'ERA5 Hourly'

    var = out.createVariable('wind^2','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['ERA5_ws2']),[2,1,0]))
    var.Long_name = 'Second moment wind speed'
    var.Units = '(ms-1)^2'
    var.dataset = 'ERA5 Hourly'

    var = out.createVariable('tos','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['model_tos']),[2,1,0]))
    var.Long_name = 'Sea surface temperature'
    var.Units = 'degC'
    var.dataset = 'Model temperature'

    var = out.createVariable('sos','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['model_sos']),[2,1,0]))
    var.Long_name = 'Sea surface salinity'
    var.Units = 'psu'
    var.dataset = 'Model salinity'

    var = out.createVariable('model_sfco2','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['model_sfco2']),[2,1,0]))
    var.Long_name = 'Model surface ocean fCO2'
    var.Units = 'uatm'

    var = out.createVariable('xco2atm','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['GCB_xCO2']),[2,1,0]))
    var.Long_name = 'Atmospheric xCO2'
    var.Units = 'ppm'
    var.dataset = 'GCB provide xCO2atm (global average monthly)'

    var = out.createVariable('fco2atm','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['atm_fco2']),[2,1,0]))
    var.Long_name = 'Fugacity of CO2 in atmosphere'
    var.Units = 'uatm'
    var.dataset = 'GCB provide xCO2atm (global average monthly) converted to fCO2atm with ERA5 sea level pressure'

    var = out.createVariable('model_flux','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['flux']),[2,1,0]))
    var.Long_name = 'Model Air-sea CO2 flux'
    var.Units = 'g C m-2 d-1'
    var.direction = '-ve into the oceans'

    var = out.createVariable('area','f4',('lat','lon'))
    var[:] = du.area_grid(lat = lat,lon = lon,res=1) * 1e6
    var.Long_name = 'Total surface area of each grid cell'
    var.Units = 'm2'
    var.description = 'Calculated assuming the Earth is a oblate sphere with major and minor radius of 6378.137 km and 6356.7523 km respectively'
    var.comment = 'Multiply "area" and "mask_sfc" to get true area used in flux calculations.'

    var = out.createVariable('mask_sfc','f4',('lat','lon'))
    var[:] = lon_switch_2d(np.transpose(mask_sfc,(1,0)))
    var.Long_name = 'Fractional coverage of ocean in each grid tile'
    var.Units = ''
    var.description = 'This is the ocean proportion mask calculated from GEBCO2023 data. '

    var = out.createVariable('model_dfco2','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['dfCO2']),[2,1,0]))
    var.Long_name = 'Model delta fCO2'
    var.Units = 'uatm'
    var.direction = '-ve indicates seawater is less than atmospheric fCO2'

    var = out.createVariable('schmidt','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['schmidt']),[2,1,0]))
    var.Long_name = 'Schmidt number for air-sea CO2 flux calculation'
    var.Units = 'unitless'
    var.description = 'Calculated from model temperature'

    var = out.createVariable('solubility','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['solubility']),[2,1,0]))
    var.Long_name = 'Solubility for air-sea CO2 flux calculation'
    var.Units = 'mol L-1 atm-1'
    var.description = 'Calculated from model temperature and salinity'

    var = out.createVariable('gas_transfer','f4',('time','lat','lon'))
    var[:] = lon_switch(np.transpose(np.array(c['k']),[2,1,0]))
    var.Long_name = 'Gas transfer coefficient at the Schmidt number'
    var.Units = 'cm hr-1'
    var.description = 'Calculated from ERA5 winds using a = 0.271'
    var.formulation = '(660/Schmidt)^-0.5 * kw'
    c.close()

    for j in data_folds:
        if i in j:
            pro = j.split('_')
            c = Dataset(os.path.join(data_prod_location,j,j+'.nc'),'r')
            time2 = np.array(c['time'])

            flux = np.zeros((len(time),len(lat),len(lon))); flux[:] = np.nan
            sfco2 = np.copy(flux)
            dfco2 = np.copy(flux)
            f = np.where(time2[0] == time)[0][0]
            print(f)
            flux[f:,:,:] = lon_switch(np.transpose(np.array(c['flux']),[2,1,0]))
            sfco2[f:,:,:] = lon_switch(np.transpose(np.array(c['model_sfco2']),[2,1,0]))
            dfco2[f:,:,:] = lon_switch(np.transpose(np.array(c['dfCO2']),[2,1,0]))
            var = out.createVariable(pro[0]+'_flux','f4',('time','lat','lon'))
            var[:] = flux
            var.Long_name = pro[0]+' Air-sea CO2 flux'
            var.Units = 'g C m-2 d-1'
            var.direction = '-ve into the oceans'
            var.data_from = os.path.join(data_prod_location,j,j+'.nc')

            var = out.createVariable(pro[0]+'_sfco2','f4',('time','lat','lon'))
            var[:] = sfco2
            var.Long_name = pro[0]+' surface ocean fCO2'
            var.Units = 'uatm'
            var.data_from = os.path.join(data_prod_location,j,j+'.nc')

            var = out.createVariable(pro[0]+'_dfco2','f4',('time','lat','lon'))
            var[:] = dfco2
            var.Long_name = pro[0]+' delta fCO2'
            var.Units = 'uatm'
            var.data_from = os.path.join(data_prod_location,j,j+'.nc')

            c.close()
    out.close()
