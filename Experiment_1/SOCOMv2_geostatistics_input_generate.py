#!/usr/bin/env python3
import numpy as np
import datetime
from netCDF4 import Dataset
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from dateutil.relativedelta import relativedelta

import sys

oceanicu_frame = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'

sys.path.append(os.path.join(oceanicu_frame))
sys.path.append(os.path.join(oceanicu_frame,'Data_Loading'))
import weight_stats as ws
import neural_network_train as nnt

def flip_lon(data):
    tem2 = np.ones((data.shape))
    tem2[:,:,0:180] = data[:,:,180:]
    tem2[:,:,180:] = data[:,:,0:180]
    return tem2

start_yr = 1990
end_yr = 2023

data_loc = 'F:/Data/GCB/2024'
data_loc_2 = 'D:/Data/GCB/2023'
#socat_file = 'D:/Data/_DataSets/SOCAT/v2023/SOCATv2023_tracks_gridded_monthly.nc'
socat_file = 'E:/Data/_Datasets/SOCAT/v2024/SOCATv2024_reanalysed_v1/SOCATv2024_ESACCIv3_biascorrected.nc'
output_file = 'output.nc'
files = glob.glob(os.path.join(data_loc,'*.nc'))
print(files)

delta = datetime.datetime(1959,1,1,0,0,0)
vars = ['sfco2','fco2atm','fgco2']
p = 0

for va in vars:
    output = {}
    names = []
    print(va)
    for v in files:
        print(v)
        s = v.split('_')
        names.append(s[2]+'_'+va)
        try:
            c = Dataset(v,'r')

            if p == 0:
                lat = np.array(c['lat'])
                lon = np.array(c['lon'])-180
            data = np.squeeze(np.array(c[va]))
            data[data<-100] = np.nan
            data[data>2000] = np.nan
            if va == 'sfco2':
                data[data<25] = np.nan
            data = flip_lon(data)
            if va == 'fgco2':
                data = data * 12.011 *(60*60*24) # mol -> g --- sec -> day
            # c.close()

            # spl = v.split('\\')
            # print(spl)
            # print(os.path.join(data_loc_2,spl[-1]))
            # c = Dataset(os.path.join(data_loc_2,spl[-1]),'r')
            time = np.array(c['time'])
            c.close()

            yrs = np.ones((len(time)))
            for i in range(len(time)):
                #print(int(time[i]))
                yrs[i] = (delta + datetime.timedelta(days=int(time[i]))).year

            f = np.where((yrs >= start_yr) & (yrs <= end_yr))[0]

            output[s[2]+'_'+va] = data[f,:,:]
        except:
            print(f'Variable: {va} does not exist in file... Generating blank entry')
            output[s[2]+'_'+va] = np.zeros((len(f),len(lat),len(lon)))

    l = output[names[0]].shape
    # geo = np.ones((l[0],l[1],l[2],len(files)))
    #
    # for i in range(len(files)):
    #     geo[:,:,:,i] = output[names[i]]
    #
    # for i in range(l[0]):
    #     na = np.squeeze(np.isnan(geo[i,:,:,:]))
    #     na = np.sum(na,axis=2)
    #     f = np.where(na != 0)
    #     #print(f)
    #     geo[i,f[0],f[1],:] = np.nan
    #
    # for i in range(len(files)):
    #     output[names[i]] = geo[:,:,:,i]

    time_o = np.ones((l[0]))
    yr = start_yr
    mon = 1
    t=0
    while yr<=end_yr:
        time_o[t] = (datetime.datetime(int(yr),int(mon),15) - datetime.datetime(1970,1,15)).days
        t = t+1
        mon=mon+1
        if mon ==13:
            yr = yr+1
            mon=1
    if p == 0:
        out_file = Dataset(output_file,mode='w',format='NETCDF4_CLASSIC')
        time = out_file.createDimension('time', l[0])
        lat2 = out_file.createDimension('lat', l[1])
        lon2 = out_file.createDimension('lon', l[2])

        var = out_file.createVariable('latitude',np.float32,('lat'))
        var[:] = lat
        var = out_file.createVariable('longitude',np.float32,('lon'))
        var[:] = lon
        var = out_file.createVariable('time',np.float32,('time'))
        var[:] = time_o
        var.units = 'Days since 1970-01-15'
        p= 1
    else:
        out_file = Dataset(output_file,mode='a',format='NETCDF4_CLASSIC')
    for key in output.keys():
        print(key)
        var = out_file.createVariable(key,np.float32,('lon','lat','time'))
        var[:] = np.transpose(output[key],[2,1,0])
    out_file.close()

# """
# Adding JMA-MLS data provided by Christian Rodenbeck
# """
# output = {}
# jm_loc = 'D:/Data/GCB/2023/Dan-share'
#
# yrs = []
# yr = 1959
# mon = 1
# while yr <= 2022:
#     yrs.append(yr)
#     mon=mon+1
#     if mon == 13:
#         yr = yr+1
#         mon=1
# yrs = np.array(yrs)
# print(yrs)
# f = np.where((yrs >= start_yr) & (yrs <= end_yr))[0]
# print(f)
# #pco2
# c = Dataset(os.path.join(jm_loc,'INPUT_paCO2_monthly+YRVI-YRVE_1x1.nc'))
# pco2atm = np.array(c['paCO2'])
# c.close()
# pco2atm = pco2atm[f,:,:]*0.996
# output['Jena-MLS_fco2atm'] = pco2atm
#
# c = Dataset(os.path.join(jm_loc,'mu1.0_300_pCO2_monthly+YRVI-YRVE_1x1.nc'))
# fco2sw = np.array(c['pCO2'])
# c.close()
# fco2sw = fco2sw[f,:,:]*0.996
# fco2sw[fco2sw<25] = np.nan
# output['Jena-MLS_sfco2'] = fco2sw
#
# c = Dataset(os.path.join(jm_loc,'mu1.0_300_ocCO2_monthly+YRVI-YRVE_1x1.nc'))
# area = np.squeeze(np.array(c['area'])[1,:,:])
#
# flux = np.array(c['ocCO2'])
# area = area[np.newaxis,:,:]
# c.close()
# flux = (flux[f,:,:] /area /365.25) * 10**12 * 12.011
# output['Jena-MLS_fgco2'] = -flux
#
#
# out_file = Dataset(output_file,mode='a',format='NETCDF4_CLASSIC')
# for key in output.keys():
#     print(key)
#     var = out_file.createVariable(key,np.float32,('lon','lat','time'))
#     var[:] = np.transpose(output[key],[2,1,0])
# out_file.close()
# """
# End of JMA-MLS data addition
#"""
"""
UoEx-Watson addition
UoEx-Watson needs the alpha variables for the skin and subskin values, to calculate delta concentration
and base the unc on delta concentration instead of dfCO2.
"""
# print(output.keys())
# coin_data = output['UoEX-UEPFFNU_fgco2']
# print(coin_data)
# print(coin_data.shape)
files = ['F:/Data/GCB/2024/full/GCB-2024_dataprod_UExP-FNN-U-v2_1985-2023.nc']
vars = ['sfco2','fco2atm','fgco2','alpha','alpha_skin']
p=0
delta = datetime.datetime(1985,1,1)
for va in vars:
    output = {}
    names = []
    print(va)
    for v in files:
        print(v)
        s = v.split('_')
        names.append(s[2]+'_'+va)
        c = Dataset(v,'r')

        if p == 0:
            lat = np.array(c['lat'])
            lon = np.array(c['lon'])-180
            #time = np.array(c['time'])
        data = np.squeeze(np.array(c[va]))
        data[data<-100] = np.nan
        data[data>2000] = np.nan
        if va == 'sfco2':
            data[data<25] = np.nan
        data = flip_lon(data)

        if va == 'fgco2':
            data = data * 12.011 *(60*60*24) # mol -> g --- sec -> day
        c.close()
        spl = v.split('\\')
        print(spl)
        print(os.path.join(data_loc_2,spl[-1]))
        c = Dataset(os.path.join(data_loc_2,spl[-1]),'r')
        time = np.array(c['time'])
        c.close()
        yrs = np.ones((len(time)))
        for i in range(len(time)):
            #print(int(time[i]))
            yrs[i] = (delta + relativedelta(months=int(time[i]))).year

        f = np.where((yrs >= start_yr) & (yrs <= end_yr))[0]
        data = data[f,:,:]
        # print(data.shape)
        # print(coin_data.shape)
        #data[np.isnan(coin_data) == 1] = np.nan
        output[s[2]+'_'+va] = data
    out_file = Dataset(output_file,mode='a',format='NETCDF4_CLASSIC')
    for key in output.keys():
        print(key)
        var = out_file.createVariable(key,np.float32,('lon','lat','time'))
        var[:] = np.transpose(output[key],[2,1,0])
    out_file.close()

#As UoEX-Watson has a smaller areal coverage, have to run through all the data and remove more...
# out_file = Dataset(output_file,mode='a')
# data = np.array(out_file['UoEX_sfco2'])
# keys = list(out_file.variables.keys())
# for v in keys:
#     print(v)
#     if (v != 'latitude') and (v != 'longitude') and (v != 'time'):
#         temp = np.array(out_file[v])
#         temp[np.isnan(data) == 1] = np.nan
#         out_file[v][:] = temp
#
# data = np.array(out_file['CMEMS-LSCE-FFNN_sfco2'])
# keys = list(out_file.variables.keys())
# for v in keys:
#     print(v)
#     if (v != 'latitude') and (v != 'longitude') and (v != 'time'):
#         temp = np.array(out_file[v])
#         temp[np.isnan(data) == 1] = np.nan
#         out_file[v][:] = temp
# out_file.close()
"""
End UoEx-Watson addition

Adding SOCAT data output file
"""
vars = ['fco2_ave_unwtd','fco2_ave_weighted','fco2_reanalysed_ave_unwtd','fco2_reanalysed_ave_weighted']
soc = {}
c = Dataset(socat_file,'r')
time = np.array(c['tmnth'])
for v in vars:
    soc[v] = np.array(c[v])

    #soc[v] = tem2
    soc[v][soc[v] < 0] = np.nan
c.close()

yrs = np.ones((len(time)))
for i in range(len(time)):
    #print(int(time[i]))
    yrs[i] = (datetime.datetime(1970,1,1,0,0,0) + datetime.timedelta(days=int(time[i]))).year
f = np.where((yrs >= start_yr) & (yrs <= end_yr))[0]

for v in vars:
    soc[v] = soc[v][f,:,:]

out_file = Dataset(output_file,mode='a')
for key in soc.keys():
    var = out_file.createVariable(key,np.float32,('lon','lat','time'))
    var[:] = np.transpose(soc[key],[2,1,0])
out_file.close()


"""
End adding SOCAT data
"""
# """
# Start OceanSODA atmospheric fCO2 subsitution
# """
# out_file = Dataset(output_file,mode='a')
# out_file['OceanSODA-ETHZ_fco2atm'][:] = out_file['CMEMS-LSCE-FFNN_fco2atm'][:]
# out_file['OceanSODA-ETHZ_fco2atm'].comment = 'Copy of CMEMS-LSCE-FFNN_fco2atm'
# out_file.close()
# """
# End OceanSODA atmospheric fCO2 susbsitution
# """
"""
Start plotting
"""
fig = plt.figure(figsize=(25,25))
gs = GridSpec(3,3, figure=fig, wspace=0.3,hspace=0.3,bottom=0.1,top=0.95,left=0.10,right=0.98)
ax = [fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[0,2]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1]),fig.add_subplot(gs[1,2]),fig.add_subplot(gs[2,0]),fig.add_subplot(gs[2,1]),fig.add_subplot(gs[2,2])]
c = Dataset(output_file,'a')
socat_fco2 = np.array(c['fco2_ave_weighted'])
keys = list(c.variables.keys())

matching = [s for s in keys if "sfco2" in s]
print(matching)
t = 0
lim = np.array([0,1000])
for va in matching:
    if va == 'UExP-FNN-U-v2_sfco2':
        print('Needs dif approach')
        s = va.split('_')
        socat_fco2_2 = np.array(c['fco2_reanalysed_ave_weighted'])
        data = np.array(c[va])
        fco2_atm = np.array(c[s[0]+'_fco2atm'])
        alpha = np.array(c[s[0]+'_alpha'])
        alpha_skin = np.array(c[s[0]+'_alpha_skin'])
        ax[t].scatter(socat_fco2_2,data,c='r')
        nnt.unweight(socat_fco2_2.ravel(),data.ravel(),ax[t],lim)
        stats_un = ws.unweighted_stats(socat_fco2_2.ravel(),data.ravel(),va)
        print(stats_un)
        ax[t].plot(lim,lim,'k-')
        ax[t].plot(lim,lim*stats_un['slope'] + stats_un['intercept'],'k--')
        ax[t].set_title(va)
        ax[t].set_xlabel('in situ reanalysed fCO$_{2 (sw)}$ ($\mu$atm)')
        ax[t].set_ylabel('Predicted fCO$_{2 (sw)}$ ($\mu$atm)')
        conc = (alpha*data)
        data = (stats_un['rmsd'] / np.abs(data)) * conc
        data = data/ np.abs(conc - (fco2_atm*alpha_skin))
        #data = stats_un['rmsd'] / np.abs((data - fco2_atm)
        data[np.isinf(data) == 1] = 10000
        data[data > 10000] = 10000
    else:
        s = va.split('_')
        data = np.array(c[va])
        #fco2_atm = np.array(c[s[0]+'_fco2atm']) # Temp replace of fco2atm so I can run results...
        fco2_atm = np.array(c['UExP-FNN-U-v2_fco2atm'])
        ax[t].scatter(socat_fco2,data)
        nnt.unweight(socat_fco2.ravel(),data.ravel(),ax[t],lim)
        stats_un = ws.unweighted_stats(socat_fco2.ravel(),data.ravel(),va)
        print(stats_un)
        ax[t].plot(lim,lim,'k-')
        ax[t].plot(lim,lim*stats_un['slope'] + stats_un['intercept'],'k--')
        ax[t].set_title(va)
        ax[t].set_xlabel('in situ fCO$_{2 (sw)}$ ($\mu$atm)')
        ax[t].set_ylabel('Predicted fCO$_{2 (sw)}$ ($\mu$atm)')
        data = stats_un['rmsd'] / np.abs(data - fco2_atm)
        data[np.isinf(data) == 1] = 10000
        data[data > 10000] = 10000
    ax[t].set_xlim(lim)
    ax[t].set_ylim(lim)
    if s[0]+'_unc' in keys:
        c[s[0]+'_unc'][:] = data
    else:
        var = c.createVariable(s[0]+'_unc',np.float32,('lon','lat','time'))
        var[:] = data
    t=t+1
fig.savefig(os.path.join('plots','validation.png'),format='png',dpi=300)
c.close()
