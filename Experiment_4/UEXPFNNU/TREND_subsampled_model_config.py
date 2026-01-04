#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 03/2023

"""
#This is needed or the code crashes with the reanalysis step...
if __name__ == '__main__':
    import os
    import sys
    os.chdir('C:\\Users\\df391\\OneDrive - University of Exeter\\Post_Doc_ESA_Contract\\OceanICU')

    print(os.getcwd())
    print(os.path.join(os.getcwd(),'Data_Loading'))

    sys.path.append(os.path.join(os.getcwd(),'Data_Loading'))
    sys.path.append(os.path.join(os.getcwd()))
    import data_utils as du
    create_inp =True
    run_neural =True

    model_save_loc = 'E:/SOCOMV2/EX4/UExPFNNU/with_trend_v2'
    inps = os.path.join(model_save_loc,'inputs')
    data_file = os.path.join(inps,'neural_network_input.nc')
    start_yr = 1985
    end_yr = 2022
    log,lag = du.reg_grid(lat=1,lon=1)

    if create_inp:
        from neural_network_train import make_save_tree
        make_save_tree(model_save_loc)
        # cur = os.getcwd()
        # from Data_Loading.interpolate_noaa_ersl import interpolate_noaa
        # interpolate_noaa('D:/Data/NOAA_ERSL/2024_download.txt',grid_lon = log,grid_lat = lag,out_dir = os.path.join(inps,'xco2atm'),start_yr=start_yr,end_yr = end_yr)
        import Data_Loading.gebco_resample as ge
        ge.gebco_resample('F:/Data/Bathymetry/GEBCO_2023.nc',log,lag,save_loc = os.path.join(inps,'bath.nc'),save_loc_fluxengine = os.path.join(inps,'fluxengine_bath.nc'))

        import construct_input_netcdf as cinp
        model_location = 'E:/SOCOMV2/EX4/inputs'
        #Vars should have each entry as [Extra_Name, netcdf_variable_name,data_location,produce_anomaly]
        vars = [['model','sst',os.path.join(model_location,'sst','%Y_%m*.nc'),1],
        ['model','sss',os.path.join(model_location,'sss','%Y_%m*.nc'),1],
        ['model','mld',os.path.join(model_location,'mld','%Y_%m*.nc'),1],
        #['model','fice',os.path.join(model_location,'fice','%Y_%m*.nc'),1],
        ['model_full','fco2_w_trend',os.path.join(model_location,'fco2_w_trend','%Y_%m*.nc'),0],
        ['model','xco2_w_trend',os.path.join(model_location,'xco2_w_trend','%Y_%m*.nc'),1],
        ['Takahashi','taka','F:/Data/Takahashi_Clim/monthly/takahashi_%m_.nc',0]
        ]
        cinp.driver(data_file,vars,start_yr = start_yr,end_yr = end_yr,lon = log,lat = lag)
        import run_reanalysis as rean
        socat_file = 'E:/SOCOMV2/EX4/SOCOMv2_hump_experiment_sampled_inputs_socatv2023_1982-2022_v4.nc'
        rean.model_fco2_append(socat_file,data_file,start_yr = start_yr,end_yr=end_yr,name = 'model',ref_yr=1982,var_name = 'fco2_w_trend')
        # #
        # #
        # cinp.fill_with_var(model_save_loc,'CCMP_ws','ERA5_si10',log=log,lag=lag)
        # cinp.fill_with_var(model_save_loc,'CCMP_ws^2','ERA5_si10',log=log,lag=lag,mod ='power2')
        # cinp.land_clear(model_save_loc)
        import self_organising_map as som
        som.som_feed_forward(model_save_loc,data_file,['model_full_fco2_w_trend','model_sst','model_sss','model_mld'])
        cinp.append_longhurst_prov(model_save_loc,'F:/Data/Longhurst/Longhurst_1_deg.nc',[1],16,'prov_smoothed')
        # cinp.append_longhurst_prov(model_save_loc,'F:/Data/Longhurst/Longhurst_1_deg.nc',[16,25],16,'prov_smoothed')
        cinp.manual_prov(model_save_loc,[35,50],[44,60],'prov_smoothed')
        cinp.manual_prov(model_save_loc,[40,48],[27,43],'prov_smoothed')

    if run_neural:
        import neural_network_train as nnt
        nnt.driver(data_file,fco2_sst = 'model', prov = 'prov_smoothed',var = ['model_sst','model_xco2_w_trend','model_sss','model_mld','model_sst_anom','model_xco2_w_trend_anom','model_sss_anom','model_mld_anom'],
           model_save_loc = model_save_loc +'/',unc =[0.15,1,0.1,0.05,0.15,1,0.1,0.05],bath = 'GEBCO_elevation',bath_cutoff = None,fco2_cutoff_low = 50,fco2_cutoff_high = 750,sea_ice = None,
           tot_lut_val=300,socat_sst=False)
        nnt.plot_total_validation_unc(fco2_sst = 'model',model_save_loc = model_save_loc,ice = None,prov='prov_smoothed')
        nnt.plot_mapped(model_save_loc)
