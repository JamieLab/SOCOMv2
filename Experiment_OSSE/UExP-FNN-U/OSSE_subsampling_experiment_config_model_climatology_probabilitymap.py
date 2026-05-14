#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 27/04/2026
Code for running the OSSE experiments under SOCOM.
"""
#This is needed or the code crashes with the reanalysis step...
def make_final_file(output_loc,locat,osse_no,configuration,model,version,start_yr,end_yr,year = '2026'):

    c = Dataset(os.path.join(locat,'output.nc'))
    lon = np.array(c['longitude'])
    lat = np.array(c['latitude'])
    fco2 = np.array(c['fco2'])
    time = np.array(c['time'])
    c.close()

    fco2 = du.lon_switch(np.transpose(fco2,[2,1,0]))
    lon = lon+180

    file = os.path.join(output_loc,'OSSE'+osse_no+'-'+year+'_'+configuration+'_UExP-FNN-U-v'+version+'_'+model+'_'+start_yr+'-'+end_yr+'.nc')
    outp = Dataset(file,'w',format='NETCDF4_CLASSIC')
    outp.date_created = datetime.datetime.now().strftime(('%d/%m/%Y'))
    outp.created_by = 'Daniel J. Ford (d.ford@exeter.ac.uk), Jamie D. Shutler (j.d.shutler@exeter.ac.uk) and Andrew Watson (Andrew.Watson@exeter.ac.uk)'
    outp.created_from = 'Data created from ' + locat
    outp.method_citation = 'Watson, A.J., Schuster, U., Shutler, J.D. et al. Revised estimates of ocean-atmosphere CO2 flux are consistent with ocean carbon inventory. Nat Commun 11, 4422 (2020). https://doi.org/10.1038/s41467-020-18203-3'
    outp.method_citation_updates = 'Ford, D. J., Blannin, J., Watts, J., Watson, A. J., Landschützer, P., Jersild, A., & Shutler, J. D. (2024). A comprehensive analysis of air-sea CO2 flux uncertainties constructed from surface ocean data products. Global Biogeochemical Cycles, 38, e2024GB008188. https://doi.org/10.1029/2024GB008188'
    outp.code_version = 'v2026-pre1'
    outp.code_github = 'https://github.com/JamieLab/OceanICU'
    outp.version = 'v'+version
    outp.time_packaged = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    outp.createDimension('lon',lon.shape[0])
    outp.createDimension('lat',lat.shape[0])
    outp.createDimension('time',time.shape[0])

    sst_o = outp.createVariable('sfco2','f4',('time','lat','lon'),fill_value=np.nan,zlib=True)
    sst_o[:] = fco2
    sst_o.units = 'uatm'
    sst_o.standard_name = 'Surface ocean fCO2'

    sst_o = outp.createVariable('lat','f4',('lat'))
    sst_o[:] = lat
    sst_o.units = 'Degrees'
    sst_o.standard_name = 'Latitude'

    sst_o = outp.createVariable('lon','f4',('lon'))
    sst_o[:] = lon
    sst_o.units = 'Degrees'
    sst_o.standard_name = 'Longitude'

    sst_o = outp.createVariable('time','f4',('time'))
    sst_o[:] = time
    sst_o.units = 'Days since 1970-01-15'
    sst_o.standard_name = 'Time'

    outp.close()
if __name__ == '__main__':
    import os
    import sys
    import datetime
    import numpy as np
    from netCDF4 import Dataset
    import gc
    oceanicu_framework = 'C:\\Users\\df391\\OneDrive - University of Exeter\\Post_Doc_ESA_Contract\\OceanICU'


    sys.path.append(os.path.join(oceanicu_framework,'Data_Loading'))
    sys.path.append(os.path.join(oceanicu_framework))
    import data_utils as du

    working_loc = 'D:/OSSE_Experiments'
    UExP_loc = os.path.join(working_loc,'UExP-FNN-U'); du.makefolder(UExP_loc)
    final_output = os.path.join(UExP_loc,'final_output'); du.makefolder(final_output)

    models = {'FESOM2_REcoM': 'FESOM2-REcoM',
            'IPSL_NEMO_PISCES': 'IPSL-NEMO-PISCES',
            'MRI_ESM2': 'MRI-ESM2'}


    configurations = {'Base':['BASELINE','1'],
                    'Base+ALL':['Base+ALL','2'],
                    'Base+Disc':['Base+Disc','3'],
                    'Base+VOS':['Base+VOS','4'],
                    'Base+RV':['Base+RV','5']}
    version = '1'
    start_yr = 1980
    end_yr = 2024
    log,lag = du.reg_grid(lat=1,lon=1)



    create_inp =True
    run_neural =True


    for con in list(configurations.keys()):
        for model in list(models.keys()):

            model_save_loc = os.path.join(UExP_loc,con+'_'+model)
            if not os.path.exists(model_save_loc):
                inps = os.path.join(model_save_loc,'inputs')
                data_file = os.path.join(inps,'neural_network_input.nc')

                if create_inp:
                    from neural_network_train import make_save_tree
                    make_save_tree(model_save_loc)
                    import Data_Loading.ESA_CCI_land as landcci
                    landcci.generate_land_cci('E:/Data/Land-CCI/ESACCI-LC-L4-WB-Map-150m-P13Y-2000-v4.0.nc','E:/Data/Land-CCI/ESACCI-LC-L4-WB-Ocean-Map-150m-P13Y-2000-v4.0.tif',log,lag,os.path.join(inps,'bath.nc'))


                    import construct_input_netcdf as cinp
                    model_location = os.path.join(working_loc,'Truth',model)
                    #Vars should have each entry as [Extra_Name, netcdf_variable_name,data_location,produce_anomaly]
                    vars = [['model','tos',os.path.join(model_location,'tos','%Y_%m*.nc'),1],
                    ['model','sos',os.path.join(model_location,'sos','%Y_%m*.nc'),1],
                    ['model','mld',os.path.join(model_location,'mld','%Y_%m*.nc'),1],
                    ['model','chl',os.path.join(model_location,'chl','%Y_%m*.nc'),1],
                    # ['model','fice',os.path.join(model_location,'fice','%Y_%m*.nc'),0],
                    ['model_full','sfco2',os.path.join(model_location,'sfco2','%Y_%m*.nc'),0],
                    ['model','xco2',os.path.join(model_location,'xco2','%Y_%m*.nc'),1],

                    ]
                    cinp.driver(data_file,vars,start_yr = start_yr,end_yr = end_yr,lon = log,lat = lag,copts={"zlib":True,})
                    import run_reanalysis as rean
                    socat_file = os.path.join(working_loc,con,model,con+'_sfco2_'+models[model]+'_1980_2024.nc')
                    rean.model_fco2_append(socat_file,data_file,start_yr = start_yr,end_yr=end_yr,name = 'model',ref_yr=1980)

                    import self_organising_map as som
                    som.som_feed_forward_probability(model_save_loc,data_file,['model_full_sfco2','model_tos','model_sos','model_mld','model_chl'],unc = [20,0.45,0.3,0.1,0.3],data_file_out=os.path.join(model_save_loc,'inputs','som_prob.nc'),ens=400)

                    som.som_probability_append_longhurst_prov(model_save_loc,os.path.join(model_save_loc,'inputs','som_prob.nc'),'F:/Data/Longhurst/Longhurst_1_deg.nc',[16,25],16,'prov_smoothed','prov_ensemble',m=0)
                    som.som_probability_append_longhurst_prov(model_save_loc,os.path.join(model_save_loc,'inputs','som_prob.nc'),'F:/Data/Longhurst/Longhurst_1_deg.nc',[1],17,'prov_smoothed','prov_ensemble_1',m=2)
                    som.som_probability_manual_prov(model_save_loc,os.path.join(model_save_loc,'inputs','som_prob.nc'),[35,50],[44,60],'prov_smoothed','prov_ensemble_2')
                    som.som_probability_manual_prov(model_save_loc,os.path.join(model_save_loc,'inputs','som_prob.nc'),[40,48],[27,43],'prov_smoothed','prov_ensemble_2')
                    som.merge_provinces(os.path.join(model_save_loc,'inputs','som_prob.nc'),data_file,'prov_smoothed','prov_ensemble_2',out_prob='prov_ensemble')

                if run_neural:
                    import neural_network_train as nnt
                    nnt.driver(data_file,fco2_sst = 'model', prov = 'prov_smoothed',var = ['model_tos','model_xco2','model_sos','model_mld','model_chl','model_tos_anom','model_xco2_anom','model_sos_anom','model_mld_anom','model_chl_anom'],
                       model_save_loc = model_save_loc +'/',unc =[0.15,1,0.1,0.05,0.3,0.15,1,0.1,0.05,0.3],fco2_cutoff_low = 50,fco2_cutoff_high = 750,
                       tot_lut_val=2000,socat_sst=False,prob_ensemble='prov_ensemble',run_network_training = True)
                    nnt.plot_total_validation_unc(fco2_sst = 'model',model_save_loc = model_save_loc,ice = None,prov='prov_smoothed')
                    nnt.plot_mapped(model_save_loc)
                make_final_file(final_output,model_save_loc,configurations[con][1],configurations[con][0],models[model],version,str(start_yr),str(end_yr))
                gc.collect()
