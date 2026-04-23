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
#Setting up OceanICU framework to use within the work...
oceanicu_loc = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(oceanicu_loc)
sys.path.append(os.path.join(oceanicu_loc,'Data_Loading'))
import data_utils as du
import construct_input_netcdf as cinp
import fluxengine_driver as fl

force_flux = 0
# Setting up so we can retrieve the right model (tos,sos, etc) for the data product...
model_location = 'E:/SOCOMV2/EX2/Input-from-ocean-models/'
mod_dictionary = {'FESOM': 'FESOM2_REcoM',
    'CESM': 'CESM_ETHZ_r1',
    'IPSL': 'IPSL_r1',
    'MRI': 'MRI_ESM2_2',
    'NorESM': 'NorESM_vGCB2024'}
mod_keys = list(mod_dictionary.keys())
print(mod_keys)

#Flux Config - this should be the same as in SOCOMV2_setup_model_flux.py
flux_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/SOCOMv2_flux_config.conf'

#Input datasets for the flux that aren't included in the models
#This should be the same as in SOCOMV2_setup_model_flux.py
inp_loc = 'E:/SOCOMV2/EX2/flux'
wind_loc = os.path.join(inp_loc,'ws')
wind2_loc = os.path.join(inp_loc,'ws2')
atm_loc = os.path.join(inp_loc,'xCO2')
msl_loc = os.path.join(inp_loc,'msl')
output_loc = os.path.join(inp_loc,'data_products')

#Lets find all the netcdf files in the output_location (which also is the input for the data product files)/
#Intention is to dump all the files into the folder, and then create subfolders for each file to do the calculation.
#Then we can check if the folder exists, and that'll tell us if we need to do the calculations.
g = glob.glob(os.path.join(output_loc,'*.nc'))

print(g)
log,lag = du.reg_grid(lat=1,lon=1) # Regular 1 deg grid (90N to 90S, -180W to 180W). All the additional flux data and model data are already
# converted to this spatial grid (and this is how the OceanICU framework is mainly setup...)
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
    start_yr = int(a[-1].split('-')[0])
    end_yr = 2022#int(a[-1][0:4]) # So we remove the .nc part of the final split component.
    product_name = a[-2] # This the the data product groups name...
    print(start_yr)
    print(end_yr)
    print(product_name)

    #Here we setup the flux calcualtion folder for the particular data product netcdf.
    #We name the folder, data product name and the model it's intended for.
    temp_out_loc = os.path.join(output_loc,product_name+'_'+model_ref)
    data_file = os.path.join(temp_out_loc,product_name+'_'+model_ref+'.nc')
    #Make the temp folder
    print(du.checkfileexist(temp_out_loc))
    if (du.checkfileexist(temp_out_loc) == False) | (force_flux == 1):
        du.makefolder(temp_out_loc)
        #Make a folder to output the pCO2 fields from the data products into individual time point netcdf's (i.e one for each month)
        du.makefolder(os.path.join(temp_out_loc,'sfco2'))
        #Load the pCO2 field
        c = Dataset(prod,'r')
        keys = c.variables.keys()
        if 'spco2' in keys:
            data= np.array(c['spco2'])
        elif 'sfco2' in keys:
            data= np.array(c['sfco2'])
        elif 'pCO2' in keys:# CarboScope
            data = np.array(c['pCO2'])

        data[data > 10000] = np.nan; data[data <= 1] = np.nan;

        if product_name == 'CarboScope':
            data = data*0.996 # CarboScope is pCO2 where as we want fCO2(sw)
        if 'time' in keys:
            time = np.array(c['time'])
            uni = c['time'].units
        else: # CarboScope has a different name for time
            time = np.array(c['mtime'])
            uni = c['mtime'].units
        lat = np.array(c['lat'])
        lon = np.copy(log)#np.array(c['lon'])-180
        c.close()
        uni2 = uni.split(' ')
        print(uni2)
        print(uni2[-1])
        if ('-' in uni2[-1]) or ('/' in uni2[-1]):
            p = -1
        else:
            p = -2
        print(p)
        if '-' in uni2[p]:
            uni2 = uni2[p].split('-')
        elif '/' in uni2[p]:
            uni2 = uni2[p].split('/')
        ref_time = datetime.datetime(int(uni2[0]),int(uni2[1]),int(uni2[2]),0,0,0)
        print(ref_time)
        print(uni2)
        if ('Days' in uni) or ('days' in uni):
            print(uni)
            print('Days')
            for t in range(len(time)):
                time[t] = (ref_time + datetime.timedelta(days = int(time[t]))).year
        elif ('Hours' in uni) or ('hours' in uni):
            print(uni)
            print('Hours')
            for t in range(len(time)):
                time[t] = (ref_time + datetime.timedelta(hours = int(time[t]))).year
        elif ('Seconds' in uni) or ('seconds' in uni):
            print(uni)
            print('Seconds')
            for t in range(len(time)):
                time[t] = (ref_time + datetime.timedelta(seconds = int(time[t]))).year

        f = np.where(time >= start_yr)


        #Cycle through the data, and save out into individual netcdfs
        yr = start_yr
        mon = 1
        ti = f[0][0]
        while ti < data.shape[0]:
            file = os.path.join(temp_out_loc,'sfco2',str(yr)+'_'+du.numstr(mon)+'_sfco2.nc')
            temp_data = data[ti,:,:] # Extract time step (first dimension is time)
            if product_name != 'CarboScope':
                temp_data = du.lon_switch_2d(temp_data) #Switch from 0-360E to -180 to 180 W
            temp_data = temp_data.transpose() # Switch from (lat, lon) to (lon,lat)
            du.netcdf_create_basic(file,temp_data,'sfco2',lat,lon)# Save

            mon = mon+1
            if mon == 13:
                mon = 1
                yr=yr+1
            ti = ti+1 #Counter

        #Now we combine all the data together, with the model tos, sos, and fice fields for the flux calcualtions.
        cinpvars = [['ERA5','ws',os.path.join(wind_loc,'%Y','%Y_%m*.nc'),0],
        ['ERA5','ws2',os.path.join(wind2_loc,'%Y','%Y_%m*.nc'),0],
        ['ERA5','msl',os.path.join(msl_loc,'%Y','%Y_%m*.nc'),0],
        ['GCB','xCO2',os.path.join(atm_loc,'%Y_%m*.nc'),0],
        ['model','tos',os.path.join(model_location,mod_dictionary[model_ref],'tos','%Y_%m*.nc'),0],
        ['model','sos',os.path.join(model_location,mod_dictionary[model_ref],'sos','%Y_%m*.nc'),0],
        ['model','sfco2',os.path.join(temp_out_loc,'sfco2','%Y_%m*.nc'),0],
        ['model','fice',os.path.join(model_location,mod_dictionary[model_ref],'fice','%Y_%m*.nc'),0]
        ]

        # Generate the combined file
        cinp.driver(data_file,cinpvars,start_yr = start_yr,end_yr = end_yr,lon = log,lat = lag,fill_clim=False)
        # Now we make the fluxEngine input folder, where we save monthly netcdf's of all the input parameters
        du.makefolder(os.path.join(temp_out_loc,'fluxengine_input'))
        # Here we make a dictionary to throw all the data with their names in.
        direct = {}
        c = Dataset(data_file,'r')
        keys = list(c.variables.keys()) # Get all the variable names in the netcdf, which should be those that are above
        keys.remove('latitude'); keys.remove('longitude'); keys.remove('time');# Remove the ancillary bits as we don't need them
        print(keys)
        #Cycle through and extract the data into the dictionary from the data_file
        for key in keys:
            direct[key] = np.array(c.variables[key][:])
        c.close()
        # direct['ERA5_si10^2'] = direct['ERA5_si10']**2 # Need a pow2 wind speed for the gas transfer parameterisation (quick and dirty currently)
        # direct['ERA5_si10^3'] = direct['ERA5_si10']**3 # Need a pow3 wind speed for the gas transfer parameterisation (quick and dirty currently)
        #Use the OceanICU framework to generate the fluxengine input files :-)
        fl.fluxengine_individual_netcdf(os.path.join(temp_out_loc),direct,log,lag,start_yr = start_yr,end_yr = end_yr)

        return_path = os.getcwd() # Path where we are now (the escape back path)
        os.chdir(os.path.join(temp_out_loc)) #Move to the folder we are working in for the data product
        returnCode, fe = fluxengine.run_fluxengine(flux_config, start_yr, end_yr, singleRun=False,verbose=True,processLayersOff=True) # Run fluxengine
        #We do this as the config file is setup on relative paths, not absolutes (so we can reuse the same config...)
        os.chdir(return_path)# Return (lets get out of this folder...)

        # Now lets load all the flux data that fluxengine has just made... and we need the ice data
        print((end_yr-start_yr-1)*12)
        flux = fl.load_flux_var(os.path.join(temp_out_loc,'flux'),'OF',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        ice = fl.load_flux_var(os.path.join(temp_out_loc,'flux'),'P1',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        dpco2 = fl.load_flux_var(os.path.join(temp_out_loc,'flux'),'dpCO2',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        # Flux engine doesn't apply the ice scaling so we do this manually (same procedure is needed for the FluxEngine budgets tool)
        flux = flux * (1-ice)
        flux = np.transpose(flux,(1,0,2))# Now we transpose so we can save the flux back to data_file (so it can be used later...)
        ice = np.transpose(ice,(1,0,2))
        dpco2 = np.transpose(dpco2,(1,0,2))
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
            # Calcualte the annual fluxes using the OceanICU framework :-)
        fl.calc_annual_flux(temp_out_loc,log,lag,start_yr,end_yr,land_file=os.path.join(inp_loc,'bath.nc'),flux_file = data_file,save_file = os.path.join(temp_out_loc,product_name+'_'+model_ref+'.csv'))
