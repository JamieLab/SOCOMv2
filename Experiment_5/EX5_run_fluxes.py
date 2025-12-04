#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 03/2023

"""

import os
import sys
from netCDF4 import Dataset
import numpy as np
import shutil
import glob
os.chdir('C:\\Users\\df391\\OneDrive - University of Exeter\\Post_Doc_ESA_Contract\\OceanICU')

print(os.getcwd())
print(os.path.join(os.getcwd(),'Data_Loading'))

sys.path.append(os.path.join(os.getcwd(),'Data_Loading'))
sys.path.append(os.path.join(os.getcwd()))
import data_utils as du
import fluxengine_driver as fl
from neural_network_train import make_save_tree,OC4C_calc_independent_test_rmsd,add_validation_unc
import construct_input_netcdf as cinp
log,lag = du.reg_grid(lat=1,lon=1)
print('Running flux calculations....')

ref_locs = {'EXP1':'F:/OceanCarbon4Climate/WP2/SST/UExP-FNN-U_dailySST_CCISST_biascorrected',
    'EXP0':'F:/OceanCarbon4Climate/WP2/SST/UExP-FNN-U_dailySST_CCISST_biascorrected_non_reanalysed'}

inps = os.path.join('F:/OceanCarbon4Climate/WP2/SST/UExP-FNN-U_dailySST_CCISST_biascorrected','inputs')

output_loc = 'E:/SOCOMV2/EX5/Output/'
output_flux_loc = os.path.join(output_loc,'fluxes')

files = glob.glob(output_loc+'*.nc')
# files = ['E:/SOCOMV2/EX5/Output\\Ex5_2025_EXP1_dataproduct_JMA-MLR_1985-2023.nc','E:/SOCOMV2/EX5/Output\\Ex5_2025_EXP0_dataproduct_JMA-MLR_1985-2023.nc']
for file in files:
    s = file.split('_')
    print(s)
    ref_loc = ref_locs[s[2]]
    inps = os.path.join(ref_locs['EXP1'],'inputs')
    print(inps)
    model_save_loc = os.path.join(output_flux_loc,s[2]+'_'+s[4])
    if not os.path.exists(model_save_loc):
        make_save_tree(model_save_loc)
        data_file = os.path.join(model_save_loc,'inputs','neural_network_input.nc')
        start_yr = int(s[-1].split('-')[0])
        end_yr = int(s[-1].split('-')[1].split('.')[0])
        print(start_yr)
        print(end_yr)
        #
        #Vars should have each entry as [Extra_Name, netcdf_variable_name,data_location,produce_anomaly]
        vars = [['CCI_SST','analysed_sst',os.path.join(inps,'SST','%Y','%Y%m*.nc'),1]
        ,['CCI_SST','sea_ice_fraction',os.path.join(inps,'SST','%Y','%Y%m*.nc'),1]
        ,['CCI_SST','analysed_sst_uncertainty',os.path.join(inps,'SST','%Y','%Y%m*.nc'),0]
        ,['NOAA_ERSL','xCO2',os.path.join(inps,'xco2atm','%Y','%Y_%m*.nc'),1]
        ,['ERA5','blh',os.path.join(inps,'blh','%Y','%Y_%m*.nc'),0]
        ,['ERA5','d2m',os.path.join(inps,'d2m','%Y','%Y_%m*.nc'),0]
        ,['ERA5','msdwlwrf',os.path.join(inps,'msdwlwrf','%Y','%Y_%m*.nc'),0]
        ,['ERA5','msdwswrf',os.path.join(inps,'msdwswrf','%Y','%Y_%m*.nc'),0]
        ,['ERA5','msl',os.path.join(inps,'msl','%Y','%Y_%m*.nc'),0]
        ,['ERA5','t2m',os.path.join(inps,'t2m','%Y','%Y_%m*.nc'),0]
        ,['ERA5','ws',os.path.join(inps,'ws','%Y','%Y_%m*.nc'),0]
        ,['ERA5','ws2',os.path.join(inps,'ws2','%Y','%Y_%m*.nc'),0]
        ,['CMEMS','so',os.path.join(inps,'SSS','%Y','%Y_%m*.nc'),1]
        ,['CMEMS','mlotst',os.path.join(inps,'MLD','%Y','%Y_%m*.nc'),1]
        ,['CCMP','ws',os.path.join(inps,'ccmpv3.1','%Y','CCMP_3.1_ws_%Y%m*.nc'),0]
        ,['CCMP','ws^2',os.path.join(inps,'ccmpv3.1','%Y','CCMP_3.1_ws_%Y%m*.nc'),0]
        ,['OSISAF','total_standard_uncertainty',os.path.join(inps,'OSISAF','%Y','%Y%m_*_COM.nc'),0]
        ,['OSISAF','ice_conc',os.path.join(inps,'OSISAF','%Y','%Y%m_*_COM.nc'),0]
        ,['Takahashi','taka','F:/Data/Takahashi_Clim/monthly/takahashi_%m_.nc',0]
        ,['RECCAP','reccap','F:/Data/RECCAP/RECCAP2_region_masks_all_v20221025_DJF.nc',0]
        ]
        cinp.driver(data_file,vars,start_yr = start_yr,end_yr = end_yr,lon = log,lat = lag)
        vars = [['CCI_SSS','sss',os.path.join(inps,'CCISSS','%Y','%Y%m*.nc'),0]]
        cinp.driver(data_file,vars,start_yr = start_yr,end_yr = end_yr,lon = log,lat = lag,append=True,fill_clim=False)
        cinp.fill_with_var(data_file,'CCI_SSS_sss','CMEMS_so',log=log,lag=lag,calc_anom=True)
        cinp.fill_with_var(data_file,'CCMP_ws','ERA5_ws',log=log,lag=lag)
        cinp.fill_with_var(data_file,'CCMP_ws^2','ERA5_ws2',log=log,lag=lag)
        shutil.copy(os.path.join(inps,'bath.nc'),os.path.join(model_save_loc,'inputs','bath.nc'))
        cinp.land_clear(model_save_loc)
        print(s[2])
        print(os.path.join(ref_locs[s[2]],'inputs','neural_network_input.nc'))
        cinp.append_independent_test(os.path.join(ref_locs[s[2]],'inputs','neural_network_input.nc'),data_file,'CCI_SST')

        c = Dataset(file,'r')
        keys = c.variables.keys()
        if 'latitude' in keys:
            lat = np.array(c.variables['latitude'])
        else:
            lat = np.array(c.variables['lat'])
        if 'longitude' in keys:
            lon = np.array(c.variables['longitude'])-180
        else:
            lon = np.array(c.variables['lon'])-180

        if s[4] == 'CarboScope': # CarboScope is already in -180 to 180, so we convert back
            lon = lon + 180

        if s[4] == 'CarboScope':
            sfco2 = np.transpose(np.array(c.variables['pCO2']),[2,1,0]) * 0.996 #Multplication value from Christian Rodenbeck.
        else:
            sfco2 = np.transpose(np.array(c.variables['sfco2']),[2,1,0])
        c.close()
        #Added a simple check for missing/fill values.
        sfco2[sfco2<=1] = np.nan
        sfco2[sfco2>3000] = np.nan

        c = Dataset(data_file,'r')
        time = np.array(c.variables['time'])
        c.close()

        direct = {}
        if s[4] == 'CarboScope': # CarboScope data is already in -180 to 180 so doesn't need rolling.
            direct['fco2'] = sfco2
        else:
            direct['fco2'] = np.roll(sfco2,180,axis=0)
        direct['fco2_net_unc'] = np.zeros((sfco2.shape))
        direct['fco2_para_unc'] = np.zeros((sfco2.shape))
        direct['fco2_val_unc'] = np.zeros((sfco2.shape))
        direct['fco2_tot_unc'] = np.zeros((sfco2.shape))

        cinp.save_netcdf(os.path.join(model_save_loc,'output.nc'),direct,lon,lat,sfco2.shape[2],time_track=time)

        OC4C_calc_independent_test_rmsd(model_save_loc,data_file,'CCI_SST',os.path.join(model_save_loc,'output.nc'),'F:/Data/RECCAP/RECCAP2_region_masks_all_v20221025_DJF.nc','reccap',extra='_indpendent')
        add_validation_unc(model_save_loc,data_file,'RECCAP_reccap',file='OC4C_independent_test.csv')

        # FLuxes
        # No Salty Skin
        fluxengine_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU/fluxengine_config/fluxengine_config_wanninkhof_era5_scaled_nosalt.conf'
        fl.fluxengine_netcdf_create(model_save_loc,input_file = data_file,tsub='CCI_SST_analysed_sst',ws = 'ERA5_ws',ws2 = 'ERA5_ws2',seaice = 'OSISAF_ice_conc',
                 sal='CCI_SSS_sss_CMEMS_so',msl = 'ERA5_msl',xCO2 = 'NOAA_ERSL_xCO2',start_yr=start_yr,end_yr=end_yr, coare_out = os.path.join(model_save_loc,'inputs','coare'), tair = 'ERA5_t2m', dewair = 'ERA5_d2m',
                 rs = 'ERA5_msdwswrf', rl = 'ERA5_msdwlwrf', zi = 'ERA5_blh',coolskin = 'None')
        fl.fluxengine_run(model_save_loc,fluxengine_config,start_yr,end_yr)
        fl.flux_uncertainty_calc(model_save_loc,start_yr = start_yr,end_yr=end_yr,fco2_tot_unc = -1,k_perunc=0.2,unc_input_file=data_file,sst_unc='CCI_SST_analysed_sst_uncertainty',atm_unc=0.4)
        fl.calc_annual_flux(model_save_loc,lon=log,lat=lag,start_yr=start_yr,end_yr=end_yr)
        fl.fixed_uncertainty_append(model_save_loc,lon=log,lat=lag)
        if not os.path.exists(os.path.join(model_save_loc,'decorrelation','fco2_decorrelation.csv')):
            fl.variogram_evaluation(model_save_loc,output_file='fco2_decorrelation',start_yr =start_yr,end_yr=end_yr,ens=50)
        shutil.copy(os.path.join(ref_loc,'decorrelation','sst_decorrelation.csv'),os.path.join(model_save_loc,'decorrelation','sst_decorrelation.csv'))
        shutil.copy(os.path.join(ref_loc,'decorrelation','ice_decorrelation.csv'),os.path.join(model_save_loc,'decorrelation','ice_decorrelation.csv'))
        shutil.copy(os.path.join(ref_loc,'decorrelation','wind_decorrelation.csv'),os.path.join(model_save_loc,'decorrelation','wind_decorrelation.csv'))

        fl.montecarlo_flux_testing(model_save_loc,decor='fco2_decorrelation.csv',flux_var = 'flux_unc_fco2sw_val',start_yr =start_yr,end_yr=end_yr)
        fl.montecarlo_flux_testing(model_save_loc,decor='ice_decorrelation.csv',seaice=True,seaice_var='OSISAF_total_standard_uncertainty',start_yr =start_yr,end_yr=end_yr)
        fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_ph2o',start_yr =start_yr,end_yr=end_yr)
        fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_schmidt',start_yr =start_yr,end_yr=end_yr)
        fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solskin_unc',start_yr =start_yr,end_yr=end_yr)
        fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solsubskin_unc',start_yr =start_yr,end_yr=end_yr)
        fl.montecarlo_flux_testing(model_save_loc,decor='wind_decorrelation.csv',flux_var = 'flux_unc_wind',start_yr =start_yr,end_yr=end_yr)
        fl.montecarlo_flux_testing(model_save_loc,decor=[2000,1500],flux_var = 'flux_unc_xco2atm',start_yr =start_yr,end_yr=end_yr)

        if s[2] == 'EXP1':
            fluxengine_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU/fluxengine_config/fluxengine_config_wanninkhof_era5_scaled.conf'
            fl.fluxengine_netcdf_create(model_save_loc,input_file = data_file,tsub='CCI_SST_analysed_sst',ws = 'ERA5_ws',ws2 = 'ERA5_ws2',seaice = 'OSISAF_ice_conc',
                     sal='CCI_SSS_sss_CMEMS_so',msl = 'ERA5_msl',xCO2 = 'NOAA_ERSL_xCO2',start_yr=start_yr,end_yr=end_yr, coare_out = os.path.join(model_save_loc,'inputs','coare'), tair = 'ERA5_t2m', dewair = 'ERA5_d2m',
                     rs = 'ERA5_msdwswrf', rl = 'ERA5_msdwlwrf', zi = 'ERA5_blh',coolskin = 'COARE3.5')
            fl.fluxengine_run(model_save_loc,fluxengine_config,start_yr,end_yr,output_ov='flux_salty_cool_skin')
            fl.flux_uncertainty_calc(model_save_loc,start_yr = start_yr,end_yr=end_yr,fco2_tot_unc = -1,k_perunc=0.2,unc_input_file=data_file,sst_unc='CCI_SST_analysed_sst_uncertainty',atm_unc=0.4,flux_loc = 'flux_salty_cool_skin',override_output='output_flux_salty_cool_skin.nc')
            fl.calc_annual_flux(model_save_loc,lon=lon,lat=lat,start_yr=start_yr,end_yr=end_yr,flux_file = os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'),save_file=os.path.join(model_save_loc,'annual_flux_salty_cool_skin.csv'))
            fl.fixed_uncertainty_append(model_save_loc,lon=log,lat=lag,flux_file = os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'),output_file='annual_flux_salty_cool_skin.csv')


            fl.montecarlo_flux_testing(model_save_loc,decor='fco2_decorrelation.csv',flux_var = 'flux_unc_fco2sw_val',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            fl.montecarlo_flux_testing(model_save_loc,decor='ice_decorrelation.csv',seaice=True,seaice_var='OSISAF_total_standard_uncertainty',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_ph2o',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_schmidt',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solskin_unc',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solsubskin_unc',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            fl.montecarlo_flux_testing(model_save_loc,decor='wind_decorrelation.csv',flux_var = 'flux_unc_wind',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            fl.montecarlo_flux_testing(model_save_loc,decor=[2000,1500],flux_var = 'flux_unc_xco2atm',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
        #

    if os.path.exists(model_save_loc):
        data_file = os.path.join(model_save_loc,'inputs','neural_network_input.nc')
        start_yr = int(s[-1].split('-')[0])
        end_yr = int(s[-1].split('-')[1].split('.')[0])
        print(start_yr)
        print(end_yr)
        #Running the Nightingale Equivalent
        if not du.checkfileexist(os.path.join(model_save_loc,'annual_flux_night_nocoolskin.csv')):
            fluxengine_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU/fluxengine_config/fluxengine_config_night_nosaltyskin.conf'
            fl.fluxengine_netcdf_create(model_save_loc,input_file = data_file,tsub='CCI_SST_analysed_sst',ws = 'ERA5_ws',ws2 = 'ERA5_ws2',seaice = 'OSISAF_ice_conc',
                     sal='CCI_SSS_sss_CMEMS_so',msl = 'ERA5_msl',xCO2 = 'NOAA_ERSL_xCO2',start_yr=start_yr,end_yr=end_yr, coare_out = os.path.join(model_save_loc,'inputs','coare'), tair = 'ERA5_t2m', dewair = 'ERA5_d2m',
                     rs = 'ERA5_msdwswrf', rl = 'ERA5_msdwlwrf', zi = 'ERA5_blh',coolskin = 'None')
            fl.fluxengine_run(model_save_loc,fluxengine_config,start_yr,end_yr,output_ov='flux_night_nocoolskin')
            fl.flux_uncertainty_calc(model_save_loc,start_yr = start_yr,end_yr=end_yr,fco2_tot_unc = -1,k_perunc=0.2,unc_input_file=data_file,sst_unc='CCI_SST_analysed_sst_uncertainty',atm_unc=0.4,flux_loc = 'flux_night_nocoolskin',override_output='output_flux_night_nocoolskin.nc')
            fl.calc_annual_flux(model_save_loc,lon=log,lat=lag,start_yr=start_yr,end_yr=end_yr,flux_file = os.path.join(model_save_loc,'output_flux_night_nocoolskin.nc'),save_file=os.path.join(model_save_loc,'annual_flux_night_nocoolskin.csv'))
            fl.fixed_uncertainty_append(model_save_loc,lon=log,lat=lag,flux_file = os.path.join(model_save_loc,'output_flux_night_nocoolskin.nc'),output_file='annual_flux_night_nocoolskin.csv')

            # flux_output_file = 'annual_flux_night_nocoolskin.csv'
            # flux_output_loc = os.path.join(model_save_loc,'flux_night_nocoolskin')
            # flux_input_file = os.path.join(model_save_loc,'output_flux_night_nocoolskin.nc')
            # fl.montecarlo_flux_testing(model_save_loc,decor='fco2_decorrelation.csv',flux_var = 'flux_unc_fco2sw_val',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='ice_decorrelation.csv',seaice=True,seaice_var='OSISAF_total_standard_uncertainty',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_ph2o',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_schmidt',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solskin_unc',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solsubskin_unc',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='wind_decorrelation.csv',flux_var = 'flux_unc_wind',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor=[2000,1500],flux_var = 'flux_unc_xco2atm',start_yr =start_yr,end_yr=end_yr)
        else:
            print('Nightingale non-cool skin produced....')
        if s[2] == 'EXP1':
            if not du.checkfileexist(os.path.join(model_save_loc,'annual_flux_night_salty_cool_skin.csv')):
                fluxengine_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU/fluxengine_config/fluxengine_config_night.conf'
                fl.fluxengine_netcdf_create(model_save_loc,input_file = data_file,tsub='CCI_SST_analysed_sst',ws = 'ERA5_ws',ws2 = 'ERA5_ws2',seaice = 'OSISAF_ice_conc',
                         sal='CCI_SSS_sss_CMEMS_so',msl = 'ERA5_msl',xCO2 = 'NOAA_ERSL_xCO2',start_yr=start_yr,end_yr=end_yr, coare_out = os.path.join(model_save_loc,'inputs','coare'), tair = 'ERA5_t2m', dewair = 'ERA5_d2m',
                         rs = 'ERA5_msdwswrf', rl = 'ERA5_msdwlwrf', zi = 'ERA5_blh',coolskin = 'COARE3.5')
                fl.fluxengine_run(model_save_loc,fluxengine_config,start_yr,end_yr,output_ov='flux_night_salty_cool_skin')
                fl.flux_uncertainty_calc(model_save_loc,start_yr = start_yr,end_yr=end_yr,fco2_tot_unc = -1,k_perunc=0.2,unc_input_file=data_file,sst_unc='CCI_SST_analysed_sst_uncertainty',atm_unc=0.4,flux_loc = 'flux_night_salty_cool_skin',override_output='output_flux_night_salty_cool_skin.nc')
                fl.calc_annual_flux(model_save_loc,lon=log,lat=lag,start_yr=start_yr,end_yr=end_yr,flux_file = os.path.join(model_save_loc,'output_flux_night_salty_cool_skin.nc'),save_file=os.path.join(model_save_loc,'annual_flux_night_salty_cool_skin.csv'))
                fl.fixed_uncertainty_append(model_save_loc,lon=log,lat=lag,flux_file = os.path.join(model_save_loc,'output_flux_night_salty_cool_skin.nc'),output_file='annual_flux_night_salty_cool_skin.csv')


                # fl.montecarlo_flux_testing(model_save_loc,decor='fco2_decorrelation.csv',flux_var = 'flux_unc_fco2sw_val',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='ice_decorrelation.csv',seaice=True,seaice_var='OSISAF_total_standard_uncertainty',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_ph2o',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_schmidt',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solskin_unc',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solsubskin_unc',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='wind_decorrelation.csv',flux_var = 'flux_unc_wind',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor=[2000,1500],flux_var = 'flux_unc_xco2atm',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            else:
                print('Nightingale Cool Skin produced....')

    #Running Nightingale with CCMP wind speeds
    if os.path.exists(model_save_loc):
        input_loc = 'F:/OceanCarbon4Climate/GCB2025/inputs'
        data_file = os.path.join(model_save_loc,'inputs','neural_network_input.nc')


        start_yr = int(s[-1].split('-')[0])
        end_yr = int(s[-1].split('-')[1].split('.')[0])
        vars = [['CCMP','ws',os.path.join(input_loc,'ccmpv3.1','%Y','CCMP_3.1_ws_%Y%m*.nc'),0]
        ,['CCMP','ws^2',os.path.join(input_loc,'ccmpv3.1','%Y','CCMP_3.1_ws_%Y%m*.nc'),0]]
        cinp.driver(data_file,vars,start_yr = start_yr,end_yr = end_yr,lon = log,lat = lag,append=True)
        cinp.fill_with_var(data_file,'CCMP_ws','ERA5_ws',log=log,lag=lag)
        cinp.fill_with_var(data_file,'CCMP_ws^2','ERA5_ws2',log=log,lag=lag)
        print(start_yr)
        print(end_yr)
        #Running the Nightingale Equivalent
        if not du.checkfileexist(os.path.join(model_save_loc,'annual_flux_night_nocoolskin_ccmp.csv')):
            fluxengine_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU/fluxengine_config/fluxengine_config_night_nosaltyskin.conf'
            fl.fluxengine_netcdf_create(model_save_loc,input_file = data_file,tsub='CCI_SST_analysed_sst',ws = 'CCMP_ws_ERA5_ws',ws2 = 'CCMP_ws^2_ERA5_ws2',seaice = 'OSISAF_ice_conc',
                     sal='CCI_SSS_sss_CMEMS_so',msl = 'ERA5_msl',xCO2 = 'NOAA_ERSL_xCO2',start_yr=start_yr,end_yr=end_yr, coare_out = os.path.join(model_save_loc,'inputs','coare'), tair = 'ERA5_t2m', dewair = 'ERA5_d2m',
                     rs = 'ERA5_msdwswrf', rl = 'ERA5_msdwlwrf', zi = 'ERA5_blh',coolskin = 'None')
            fl.fluxengine_run(model_save_loc,fluxengine_config,start_yr,end_yr,output_ov='flux_night_nocoolskin_ccmp')
            fl.flux_uncertainty_calc(model_save_loc,start_yr = start_yr,end_yr=end_yr,fco2_tot_unc = -1,k_perunc=0.2,unc_input_file=data_file,sst_unc='CCI_SST_analysed_sst_uncertainty',atm_unc=0.4,flux_loc = 'flux_night_nocoolskin_ccmp',override_output='output_flux_night_nocoolskin_ccmp.nc')
            fl.calc_annual_flux(model_save_loc,lon=log,lat=lag,start_yr=start_yr,end_yr=end_yr,flux_file = os.path.join(model_save_loc,'output_flux_night_nocoolskin_ccmp.nc'),save_file=os.path.join(model_save_loc,'annual_flux_night_nocoolskin_ccmp.csv'))
            fl.fixed_uncertainty_append(model_save_loc,lon=log,lat=lag,flux_file = os.path.join(model_save_loc,'output_flux_night_nocoolskin_ccmp.nc'),output_file='annual_flux_night_nocoolskin_ccmp.csv')

            # flux_output_file = 'annual_flux_night_nocoolskin.csv'
            # flux_output_loc = os.path.join(model_save_loc,'flux_night_nocoolskin')
            # flux_input_file = os.path.join(model_save_loc,'output_flux_night_nocoolskin.nc')
            # fl.montecarlo_flux_testing(model_save_loc,decor='fco2_decorrelation.csv',flux_var = 'flux_unc_fco2sw_val',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='ice_decorrelation.csv',seaice=True,seaice_var='OSISAF_total_standard_uncertainty',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_ph2o',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_schmidt',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solskin_unc',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solsubskin_unc',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor='wind_decorrelation.csv',flux_var = 'flux_unc_wind',start_yr =start_yr,end_yr=end_yr)
            # fl.montecarlo_flux_testing(model_save_loc,decor=[2000,1500],flux_var = 'flux_unc_xco2atm',start_yr =start_yr,end_yr=end_yr)
        else:
            print('CCMP Nightingale non-cool skin produced....')
        if s[2] == 'EXP1':
            if not du.checkfileexist(os.path.join(model_save_loc,'annual_flux_night_salty_cool_skin_ccmp.csv')):
                fluxengine_config = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU/fluxengine_config/fluxengine_config_night.conf'
                fl.fluxengine_netcdf_create(model_save_loc,input_file = data_file,tsub='CCI_SST_analysed_sst',ws = 'CCMP_ws_ERA5_ws',ws2 = 'CCMP_ws^2_ERA5_ws2',seaice = 'OSISAF_ice_conc',
                         sal='CCI_SSS_sss_CMEMS_so',msl = 'ERA5_msl',xCO2 = 'NOAA_ERSL_xCO2',start_yr=start_yr,end_yr=end_yr, coare_out = os.path.join(model_save_loc,'inputs','coare'), tair = 'ERA5_t2m', dewair = 'ERA5_d2m',
                         rs = 'ERA5_msdwswrf', rl = 'ERA5_msdwlwrf', zi = 'ERA5_blh',coolskin = 'COARE3.5')
                fl.fluxengine_run(model_save_loc,fluxengine_config,start_yr,end_yr,output_ov='flux_night_salty_cool_skin_ccmp')
                fl.flux_uncertainty_calc(model_save_loc,start_yr = start_yr,end_yr=end_yr,fco2_tot_unc = -1,k_perunc=0.2,unc_input_file=data_file,sst_unc='CCI_SST_analysed_sst_uncertainty',atm_unc=0.4,flux_loc = 'flux_night_salty_cool_skin_ccmp',override_output='output_flux_night_salty_cool_skin_ccmp.nc')
                fl.calc_annual_flux(model_save_loc,lon=log,lat=lag,start_yr=start_yr,end_yr=end_yr,flux_file = os.path.join(model_save_loc,'output_flux_night_salty_cool_skin_ccmp.nc'),save_file=os.path.join(model_save_loc,'annual_flux_night_salty_cool_skin_ccmp.csv'))
                fl.fixed_uncertainty_append(model_save_loc,lon=log,lat=lag,flux_file = os.path.join(model_save_loc,'output_flux_night_salty_cool_skin_ccmp.nc'),output_file='annual_flux_night_salty_cool_skin_ccmp.csv')


                # fl.montecarlo_flux_testing(model_save_loc,decor='fco2_decorrelation.csv',flux_var = 'flux_unc_fco2sw_val',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='ice_decorrelation.csv',seaice=True,seaice_var='OSISAF_total_standard_uncertainty',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_ph2o',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_schmidt',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solskin_unc',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='sst_decorrelation.csv',flux_var = 'flux_unc_solsubskin_unc',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor='wind_decorrelation.csv',flux_var = 'flux_unc_wind',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
                # fl.montecarlo_flux_testing(model_save_loc,decor=[2000,1500],flux_var = 'flux_unc_xco2atm',start_yr =start_yr,end_yr=end_yr,output_file='annual_flux_salty_cool_skin.csv',fluxloc = os.path.join(model_save_loc,'flux_salty_cool_skin'),inp_file=os.path.join(model_save_loc,'output_flux_salty_cool_skin.nc'))
            else:
                print('CCMP Nightingale Cool Skin produced....')
