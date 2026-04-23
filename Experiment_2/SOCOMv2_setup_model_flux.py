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
force_flux =0

inp_loc = 'E:/SOCOMV2/EX2/flux'
wind_loc = os.path.join(inp_loc,'ws')
wind2_loc = os.path.join(inp_loc,'ws2')
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

#models = [models[0]]

log,lag = du.reg_grid(lat=1,lon=1)
for mod in models:
    print(mod)
    du.makefolder(os.path.join(output_loc,mod))
    data_file = os.path.join(output_loc,mod,'combined_variables.nc')
    # print(du.checkfileexist(temp_out_loc))
    if (du.checkfileexist(os.path.join(output_loc,mod)) == 0) | (force_flux == 1):
        # cinpvars = [['ERA5','ws',os.path.join(wind_loc,'%Y','%Y_%m*.nc'),0],
        # ['ERA5','ws2',os.path.join(wind2_loc,'%Y','%Y_%m*.nc'),0],
        # ['ERA5','msl',os.path.join(msl_loc,'%Y','%Y_%m*.nc'),0],
        # ['GCB','xCO2',os.path.join(atm_loc,'%Y_%m*.nc'),0],
        # ['model','tos',os.path.join(model_location,mod,'tos','%Y_%m*.nc'),0],
        # ['model','sos',os.path.join(model_location,mod,'sos','%Y_%m*.nc'),0],
        # ['model','sfco2',os.path.join(model_location,mod,'sfco2','%Y_%m*.nc'),0],
        # ['model','fice',os.path.join(model_location,mod,'fice','%Y_%m*.nc'),0]
        # ]
        #
        # # #
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

        # fl.fluxengine_individual_netcdf(os.path.join(output_loc,mod),direct,log,lag,start_yr = start_yr,end_yr = end_yr)
        return_path = os.getcwd()
        os.chdir(os.path.join(output_loc,mod))
        returnCode, fe = fluxengine.run_fluxengine(flux_config, start_yr, end_yr, singleRun=False,verbose=True,processLayersOff=True)
        os.chdir(return_path)
        #
        # print((end_yr-start_yr-1)*12)
        flux = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'OF',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        ice = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'P1',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        dpco2 = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'dpCO2',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        schmidt = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'SC',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        sol = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'fnd_solubility',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        pgas = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'OAPC1',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)
        k = fl.load_flux_var(os.path.join(output_loc,mod,'flux'),'OK3',start_yr,end_yr,len(log),len(lag),(end_yr-start_yr+1)*12)

        flux = flux * (1-ice)
        flux = np.transpose(flux,(1,0,2))
        ice = np.transpose(ice,(1,0,2))
        dpco2 = np.transpose(dpco2,(1,0,2))
        schmidt = np.transpose(schmidt,(1,0,2))
        sol = np.transpose(sol,(1,0,2))
        pgas = np.transpose(pgas,(1,0,2))
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

        if 'schmidt' in keys:
            c.variables['schmidt'][:] = schmidt
        else:
            var_o = c.createVariable('schmidt','f4',('longitude','latitude','time'))
            var_o[:] = schmidt
        if 'solubility' in keys:
            c.variables['solubility'][:] = sol
        else:
            var_o = c.createVariable('solubility','f4',('longitude','latitude','time'))
            var_o[:] = sol
        if 'atm_fco2' in keys:
            c.variables['atm_fco2'][:] = pgas
        else:
            var_o = c.createVariable('atm_fco2','f4',('longitude','latitude','time'))
            var_o[:] = pgas

        if 'k' in keys:
            c.variables['k'][:] = k
        else:
            var_o = c.createVariable('k','f4',('longitude','latitude','time'))
            var_o[:] = k
        c.close()

        fl.calc_annual_flux(os.path.join(output_loc,mod),log,lag,start_yr,end_yr,bath_file=os.path.join(inp_loc,'bath.nc'),flux_file = data_file,save_file = os.path.join(output_loc,mod,mod+'_full.csv'))
