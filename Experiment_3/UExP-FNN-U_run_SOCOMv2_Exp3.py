#!/usr/bin/env python3

def download_file(ensemble,loc):
    # Construct file name
    url = 'https://nyu1.osn.mghpcc.org/leap-pangeo-manual/pco2_all_members_1982-2023/post01_xgb_inputs/'+ensemble[0]+'/'+ensemble[1]+'/MLinput_'+ensemble[0]+'_'+ensemble[1].split('_')[1]+'_mon_1x1_198202_202312.pkl'
    output = os.path.join(loc,'MLinput_'+ensemble[0]+'_'+ensemble[1].split('_')[1]+'_mon_1x1_198202_202312.pkl')
    print('Downloading...')
    print(url)
    response = requests.get(url, stream=True)
    with open(output, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)
    print('Download Complete!')
    return output

def save_output_file(model_save_loc,ensemble,output_loc,start_yr,end_yr):
    c = Dataset(os.path.join(model_save_loc,'output.nc'))
    lon = np.array(c['longitude'])
    lat = np.array(c['latitude'])

    fco2 = np.transpose(np.array(c['fco2']),[2,0,1])
    fco2_net = np.transpose(np.array(c['fco2_net_unc']),[2,0,1])
    fco2_para = np.transpose(np.array(c['fco2_para_unc']),[2,0,1])
    fco2_val = np.transpose(np.array(c['fco2_val_unc']),[2,0,1])
    time = np.array(c['time'])
    c.close()

    file = os.path.join(final_output_loc,'Ex3-2025_'+ensembles[i][0]+'_'+ensembles[i][1]+'_dataprod_UExP-FNN-U_'+str(start_yr)+'_'+str(end_yr)+'.nc')
    outp = Dataset(file,'w',format='NETCDF4_CLASSIC')
    outp.date_created = datetime.datetime.now().strftime(('%d/%m/%Y'))
    outp.created_by = 'Daniel J. Ford (d.ford@exeter.ac.uk), Jamie D. Shutler (j.d.shutler@exeter.ac.uk) and Andrew Watson (Andrew.Watson@exeter.ac.uk)'
    outp.created_from = 'Data created from ' + model_save_loc
    outp.method_citation = 'Watson, A.J., Schuster, U., Shutler, J.D. et al. Revised estimates of ocean-atmosphere CO2 flux are consistent with ocean carbon inventory. Nat Commun 11, 4422 (2020). https://doi.org/10.1038/s41467-020-18203-3'
    outp.method_citation_updates = 'Ford, D. J., Blannin, J., Watts, J., Watson, A. J., Landschützer, P., Jersild, A., & Shutler, J. D. (2024). A comprehensive analysis of air-sea CO2 flux uncertainties constructed from surface ocean data products. Global Biogeochemical Cycles, 38, e2024GB008188. https://doi.org/10.1029/2024GB008188'

    outp.createDimension('lon',lon.shape[0])
    outp.createDimension('lat',lat.shape[0])
    outp.createDimension('time',time.shape[0])

    sst_o = outp.createVariable('spco2','f4',('time','lon','lat'),zlib=True)
    sst_o[:] = fco2
    sst_o.units = 'uatm'
    sst_o.standard_name = 'Surface ocean pCO2'

    sst_o = outp.createVariable('spco2_net_unc','f4',('time','lon','lat'),zlib=True)
    sst_o[:] = fco2_net
    sst_o.units = 'uatm'
    sst_o.standard_name = 'Surface ocean pCO2 network uncertainty'
    sst_o.comment = "Uncertainties considered 95% confidence (2 sigma)"

    sst_o = outp.createVariable('spco2_para_unc','f4',('time','lon','lat'),zlib=True)
    sst_o[:] = fco2_para
    sst_o.units = 'uatm'
    sst_o.standard_name = 'Surface ocean pCO2 parameter uncertainty'
    sst_o.comment = "Uncertainties considered 95% confidence (2 sigma)"

    sst_o = outp.createVariable('spco2_val_unc','f4',('time','lon','lat'),zlib=True)
    sst_o[:] = fco2_val
    sst_o.units = 'uatm'
    sst_o.standard_name = 'Surface ocean pCO2 validation uncertainty'
    sst_o.comment = "Uncertainties considered 95% confidence (2 sigma)"


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
    import pandas as pd
    import xarray
    import os
    import sys
    import numpy as np
    import shutil
    import requests
    from netCDF4 import Dataset
    import datetime
    sys.path.append(os.path.join('C:\\Users\\df391\\OneDrive - University of Exeter\\Post_Doc_ESA_Contract\\OceanICU','Data_Loading'))
    sys.path.append(os.path.join('C:\\Users\\df391\\OneDrive - University of Exeter\\Post_Doc_ESA_Contract\\OceanICU'))

    import data_utils as du

    main_loc = 'E:/SOCOMV2/EX3/'
    final_output_loc = os.path.join(main_loc,'final_output')
    du.makefolder(final_output_loc)
    bath_file = os.path.join(main_loc,'bath.nc')

    i=0
    ensembles = [
        #### CESM2: member_r10i1p1f1, member_r11i1p1f1, member_r4i1p1f1
        ['CESM2','member_r10i1p1f1'],
        ['CESM2','member_r11i1p1f1'],
        ['CESM2','member_r4i1p1f1'],
        #### CESM2-WACCM: member_r1i1p1f1, member_r2i1p1f1, member_r3i1p1f1
        ['CESM2-WACCM','member_r1i1p1f1'],
        ['CESM2-WACCM','member_r2i1p1f1'],
        ['CESM2-WACCM','member_r3i1p1f1'],
        #### CanESM5-CanOE: member_r1i1p2f1, member_r2i1p2f1, member_r3i1p2f1
        ['CanESM5-CanOE','member_r1i1p2f1'],
        ['CanESM5-CanOE','member_r2i1p2f1'],
        ['CanESM5-CanOE','member_r3i1p2f1'],
        #### UKESM1-0-LL: member_r1i1p1f2, member_r2i1p1f2, member_r3i1p1f2
        ['UKESM1-0-LL','member_r1i1p1f2'],
        ['UKESM1-0-LL','member_r2i1p1f2'],
        ['UKESM1-0-LL','member_r3i1p1f2'],
        #### CanESM5: member_r10i1p2f1, member_r1i1p1f1, member_r1i1p2f1
        ['CanESM5','member_r10i1p2f1'],
        ['CanESM5','member_r1i1p1f1'],
        ['CanESM5','member_r1i1p2f1'],
        #### MPI-ESM1-2-LR: member_r11i1p1f1, member_r12i1p1f1, member_r14i1p1f1
        ['MPI-ESM1-2-LR','member_r11i1p1f1'],
        ['MPI-ESM1-2-LR','member_r12i1p1f1'],
        ['MPI-ESM1-2-LR','member_r14i1p1f1']
    ]
    ensembles = [['ACCESS-ESM1-5','member_r5i1p1f1']]
    file = download_file(ensembles[i],main_loc)


    data = pd.read_pickle(file)
    data = data.to_xarray()


    lon = data['xlon'].data
    lat = data['ylat'].data
    vars = ['sst','sss','mld_log','xco2','spco2']
    model_save_loc = os.path.join(main_loc,ensembles[i][0]+'_'+ensembles[i][1])
    inps = os.path.join(model_save_loc,'inputs')
    data_file = os.path.join(inps,'neural_network_input.nc')
    start_yr = 1982
    end_yr = 2023
    from neural_network_train import make_save_tree
    from construct_input_netcdf import save_netcdf
    make_save_tree(model_save_loc)
    shutil.copy(bath_file,os.path.join(model_save_loc,'inputs','bath.nc'))

    # for i in vars:
    #     act_var = np.transpose(data[i].data,(1,2,0))
    #     emp = np.zeros((act_var.shape[0],act_var.shape[1],1));emp[:] = np.nan
    #     print(act_var.shape)
    #     act_var = np.concatenate((emp,act_var),axis=2)
    #     print(act_var.shape)
    #     du.makefolder(os.path.join(inps,i))
    #
    #
    #
    #     out_file= os.path.join(inps,i,'%Y_%m_'+i+'.nc')
    #
    #     yr = start_yr
    #     mon = 1
    #     t = 0
    #     while yr <=end_yr:
    #         du.netcdf_create_basic(out_file.replace('%Y',str(yr)).replace('%m',du.numstr(mon)),act_var[:,:,t],i,lat,lon)
    #         mon=mon+1
    #         t = t+1
    #         if mon == 13:
    #             yr = yr+1
    #             mon=1
    #
    #     if i == 'spco2':
    #         mask = np.transpose(data['socat_mask'].data,(1,2,0))
    #         mask = np.concatenate((emp,mask),axis=2)
    #         act_var[mask == 0] = np.nan
    #
    #         out_file= os.path.join(inps,i,'all_'+i+'.nc')
    #         direct={}
    #         direct[i] = act_var
    #         save_netcdf(out_file,direct,lon,lat,act_var.shape[2])

    import construct_input_netcdf as cinp
    #Vars should have each entry as [Extra_Name, netcdf_variable_name,data_location,produce_anomaly]
    # vars = [['model','sst',os.path.join(inps,'sst','%Y_%m*.nc'),1],
    # ['model','sss',os.path.join(inps,'sss','%Y_%m*.nc'),1],
    # ['model','mld_log',os.path.join(inps,'mld_log','%Y_%m*.nc'),1],
    # ['model','xco2',os.path.join(inps,'xco2','%Y_%m*.nc'),1],
    # ['model','spco2',os.path.join(inps,'spco2','%Y_%m*.nc'),0],
    # ['Takahashi','taka','F:/Data/Takahashi_Clim/monthly/takahashi_%m_.nc',0]
    # ]
    # cinp.driver(data_file,vars,start_yr = start_yr,end_yr = end_yr,lon = lon,lat = lat)
    # import run_reanalysis as rean
    # socat_file = os.path.join(inps,'spco2','all_spco2.nc')
    # rean.model_fco2_append(socat_file,data_file,start_yr = start_yr,end_yr=end_yr,ref_yr =1982,name = 'model',var_name='spco2',transposing=False)
    # import self_organising_map as som
    # som.som_feed_forward(model_save_loc,data_file,['Takahashi_taka','model_sst','model_sss','model_mld_log'])
    # cinp.append_longhurst_prov(model_save_loc,'F:/Data/Longhurst/Longhurst_1_deg.nc',[1],17,'prov_smoothed')
    # cinp.append_longhurst_prov(model_save_loc,'F:/Data/Longhurst/Longhurst_1_deg.nc',[16,25],16,'prov_smoothed')
    # cinp.manual_prov(model_save_loc,[35,50],[44,60],'prov_smoothed')
    # cinp.manual_prov(model_save_loc,[40,48],[27,43],'prov_smoothed')

    import neural_network_train as nnt
    # nnt.driver(data_file,fco2_sst = 'model', prov = 'prov_smoothed',var = ['model_sst','model_xco2','model_sss','model_mld_log','model_sst_anom','model_xco2_anom','model_sss_anom','model_mld_log_anom'],
    #    model_save_loc = model_save_loc +'/',unc =[0.15,1,0.1,0.05,0.15,1,0.1,0.05],fco2_cutoff_low = 50,fco2_cutoff_high = 750,sea_ice = None,
    #    tot_lut_val=300,socat_sst=False)
    # nnt.plot_total_validation_unc(fco2_sst = 'model',model_save_loc = model_save_loc,ice = None,prov='prov_smoothed')
    # nnt.plot_mapped(model_save_loc)

    save_output_file(model_save_loc,ensembles[i],final_output_loc,start_yr,end_yr)
