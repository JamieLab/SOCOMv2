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

oceanicu_loc = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(oceanicu_loc)
sys.path.append(os.path.join(oceanicu_loc,'Data_Loading'))
import data_utils as du
import construct_input_netcdf as cinp
import fluxengine_driver as fl

model_location = 'E:/SOCOMV2/EX2/Input-from-ocean-models/'
flux_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/SOCOMv2_flux_config.conf'
start_yr = 1970
end_yr = 2022

inp_loc = 'E:/SOCOMV2/EX2/flux'
wind_loc = os.path.join(inp_loc,'si10')
atm_loc = os.path.join(inp_loc,'xCO2')
msl_loc = os.path.join(inp_loc,'msl')
output_loc = os.path.join(inp_loc,'models')


model_vars = ['sfco2','tos','sos','fice']
g = glob.glob(model_location+'*')
print(g)
models = []
for i in g:
    models.append(i.split('\\')[-1])
print(models)

# models = [models[3]]
log,lag = du.reg_grid(lat=1,lon=1)
for mod in models:
    # print(mod)
    # du.makefolder(os.path.join(output_loc,mod))
    # cinpvars = [['ERA5','si10',os.path.join(wind_loc,'%Y','%Y_%m*.nc'),0],
    # ['ERA5','msl',os.path.join(msl_loc,'%Y','%Y_%m*.nc'),0],
    # ['NOAA_ERSL','xCO2',os.path.join(atm_loc,'%Y_%m*.nc'),0],
    # ['model','tos',os.path.join(model_location,mod,'tos','%Y_%m*.nc'),0],
    # ['model','sos',os.path.join(model_location,mod,'sos','%Y_%m*.nc'),0],
    # ['model','sfco2',os.path.join(model_location,mod,'sfco2','%Y_%m*.nc'),0],
    # ['model','fice',os.path.join(model_location,mod,'fice','%Y_%m*.nc'),0]
    # ]
    data_file = os.path.join(output_loc,mod,'combined_variables.nc')
    # #
    # cinp.driver(data_file,cinpvars,start_yr = start_yr,end_yr = end_yr,lon = log,lat = lag)
    # #
    # du.makefolder(os.path.join(output_loc,mod,'fluxengine_input'))
    # #
    # direct = {}
    # c = Dataset(data_file,'r')
    # keys = list(c.variables.keys())
    # keys.remove('latitude'); keys.remove('longitude'); keys.remove('time');
    # print(keys)
    # for key in keys:
    #     direct[key] = np.array(c.variables[key][:])
    # c.close()
    # direct['ERA5_si10^2'] = direct['ERA5_si10']**2
    # direct['ERA5_si10^3'] = direct['ERA5_si10']**3
    # fl.fluxengine_individual_netcdf(os.path.join(output_loc,mod),direct,log,lag,start_yr = start_yr,end_yr = end_yr)
    # return_path = os.getcwd()
    # os.chdir(os.path.join(output_loc,mod))
    # returnCode, fe = fluxengine.run_fluxengine(flux_config, start_yr, end_yr, singleRun=False,verbose=True)
    # os.chdir(return_path)
    #
    # print((end_yr-start_yr-1)*12)
    flux = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'OF',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
    ice = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'P1',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)

    flux = flux * (1-ice)
    flux = np.transpose(flux,(1,0,2))
    ice = np.transpose(ice,(1,0,2))
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
    c.close()

    fl.calc_annual_flux(os.path.join(output_loc,mod),log,lag,start_yr,end_yr,bath_file=os.path.join(inp_loc,'bath.nc'),flux_file = data_file,save_file = os.path.join(output_loc,mod,mod+'_full.csv'))
