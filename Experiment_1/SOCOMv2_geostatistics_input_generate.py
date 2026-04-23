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
end_yr = 2024

working_directory = 'D:/SOCOMv2/Experiment1/GCB2025'
data_loc = 'D:/Data/GCB2025/fCO2-product'
socat_file = 'E:/Data/_Datasets/SOCAT/v2025/SOCATv2025_v0-2/Fordetal_SOCATv2025_ESACCIv3_biascorrected_Humpherys_daily_v0-2.nc'
output_file = os.path.join(working_directory,'output_GCBv2025.nc')
reccap_file = 'F:/Data/RECCAP/RECCAP2_region_masks_all_v20221025_filled_DJF.nc'

files = glob.glob(os.path.join(data_loc,'*.nc'))
print(files)

cool_skin_prod = ['UExP-FNN-U']
recalculated_socat_prod = ['UExP-FNN-U','JMA-MLR']

vars = ['sfco2','fco2atm','fgco2']
gen_dimension = 0

for va in vars:
    output = {}
    names = []
    print(va)
    va_s = va
    for v in files:
        va = va_s
        for p in recalculated_socat_prod:
            if p in v:
                if va == 'sfco2':
                    va = 'sfco2_corrected'
                if va == 'fgco2':
                    va = 'fgco2_corrected'
                break
        print(v)
        s = v.split('_')
        names.append(s[2]+'_'+va)
        try:
            print(v + ': Loading data')
            c = Dataset(v,'r')

            if gen_dimension == 0:
                lat = np.array(c['lat'])
                lon = np.array(c['lon'])-180
                gen_dimension = 1
            data = np.squeeze(np.array(c[va]))
            data[data<-100] = np.nan
            data[data>2000] = np.nan
            data = flip_lon(data)

            if (va == 'sfco2') | (va == 'sfco2_corrected'):
                data[data<25] = np.nan

            if (va == 'fgco2') | (va == 'fgco2_corrected'):
                data = data * 12.011 *(60*60*24) # mol -> g --- sec -> day

            c.close()
            print(v + ': Data Loaded')
            print(v + ': Generating time')
            prod_year = s[-1].split('-')
            prod_start = int(prod_year[0])
            prod_end = int(prod_year[1][0:4])

            yr = prod_start
            mon = 1
            time = []
            while yr<=prod_end:
                time.append(datetime.datetime(yr,mon,15).year)
                mon=mon+1
                if mon==13:
                    yr = yr+1
                    mon = 1
            yrs = np.array(time)

            print(v + ': Time Generated')

            f = np.where((yrs >= start_yr) & (yrs <= end_yr))[0]

            output[s[2]+'_'+va_s] = data[f,:,:]
            print(v + ': Added output to dictionary')
        except:
            print(f'Variable: {va} does not exist in file... Generating blank entry')
            output[s[2]+'_'+va_s] = np.zeros((len(f),len(lat),len(lon)))
            # else:
            #     print('Cool skin product will be dealt with later: ' + v)

    l = output[names[0]].shape

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

    if gen_dimension == 1:
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
        gen_dimension = 2
    else:
        out_file = Dataset(output_file,mode='a',format='NETCDF4_CLASSIC')
    for key in output.keys():
        print(key)
        var = out_file.createVariable(key,np.float32,('lon','lat','time'))
        var[:] = np.transpose(output[key],[2,1,0])
    out_file.close()

"""
Adding JENA data provided by Christian Rodenbeck
"""
output = {}
jm_loc = os.path.join(data_loc,'JENA')
print('Adding JENA to files...')
print('Check location is correct for JENA: ' + jm_loc)

yrs = []

yr = 1957
print('Check JENA start year is correct: ' + str(yr))
mon = 1
while yr <= end_yr:
    yrs.append(yr)
    mon=mon+1
    if mon == 13:
        yr = yr+1
        mon=1
yrs = np.array(yrs)
print(yrs)
f = np.where((yrs >= start_yr) & (yrs <= end_yr))[0]
print(f)
#pco2atm
c = Dataset(os.path.join(jm_loc,'INPUT_paCO2_monthly+YRVI-YRVE_1x1.nc'))
pco2atm = np.array(c['paCO2'])
c.close()
pco2atm = pco2atm[f,:,:]*0.996
output['Jena-MLS_fco2atm'] = pco2atm
# pco2sw
c = Dataset(os.path.join(jm_loc,'oc_v2025.pCO2_monthly_1x1.nc'))
fco2sw = np.array(c['pCO2'])
c.close()
fco2sw = fco2sw[f,:,:]*0.996
fco2sw[fco2sw<25] = np.nan
output['Jena-MLS_sfco2'] = fco2sw

#flux
c = Dataset(os.path.join(jm_loc,'oc_v2025.ocCO2_monthly_1x1.nc'))
area = np.squeeze(np.array(c['area'])[1,:,:]) # Area of the ocean used by JENA

flux = np.array(c['ocCO2'])
area = area[np.newaxis,:,:]
c.close()
flux = (flux[f,:,:] /area /365.25) * 10**12 * 12.011 # Flux in Tg C yr-1, so we need to convert to g C m-2 d-1
output['Jena-MLS_fgco2'] = -flux


out_file = Dataset(output_file,mode='a',format='NETCDF4_CLASSIC')
for key in output.keys():
    print(key)
    var = out_file.createVariable(key,np.float32,('lon','lat','time'))
    var[:] = np.transpose(output[key],[2,1,0])
out_file.close()
print('JENA data added!')
"""
End of JENA data addition
"""

"""
Addition of extra variables for groups that apply the cool skin correction
Need the alpha variables for the skin and subskin values, to calculate delta concentration
and base the unc on delta concentration instead of dfCO2.
"""

vars = ['alpha','alpha_skin']

for va in vars:
    output = {}
    names = []
    print(va)
    for v in files:
        for p in cool_skin_prod:
            if p in v:

                print(v)
                s = v.split('_')
                names.append(s[2]+'_'+va)
                c = Dataset(v,'r')
                data = np.squeeze(np.array(c[va]))
                data[data<-100] = np.nan
                data[data>2000] = np.nan
                if va == 'sfco2_corrected':
                    data[data<25] = np.nan
                data = flip_lon(data)

                if va == 'fgco2_corrected':
                    data = data * 12.011 *(60*60*24) # mol -> g --- sec -> day
                c.close()

                prod_year = s[-1].split('-')
                prod_start = int(prod_year[0])
                prod_end = int(prod_year[1][0:4])

                yr = prod_start
                mon = 1
                time = []
                while yr<=prod_end:
                    time.append(datetime.datetime(yr,mon,15).year)
                    mon=mon+1
                    if mon==13:
                        yr = yr+1
                        mon = 1
                yrs = np.array(time)

                f = np.where((yrs >= start_yr) & (yrs <= end_yr))[0]
                data = data[f,:,:]
                # print(data.shape)
                # print(coin_data.shape)
                #data[np.isnan(coin_data) == 1] = np.nan
                output[s[2]+'_'+va] = data
            else:
                print('Not a cool skin product: ' + v)
    out_file = Dataset(output_file,mode='a',format='NETCDF4_CLASSIC')
    for key in output.keys():
        print(key)
        var = out_file.createVariable(key,np.float32,('lon','lat','time'))
        var[:] = np.transpose(output[key],[2,1,0])
    out_file.close()

"""
End of added additional variables needed for groups that apply the cool skin

Adding SOCAT data output file
"""
vars = ['fco2_ave_unwtd','fco2_ave_weighted','fco2_recalculated_ave_unwtd','fco2_recalculated_ave_weighted']
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

"""
Start plotting
"""
fig = plt.figure(figsize=(25,25))
gs = GridSpec(3,3, figure=fig, wspace=0.3,hspace=0.3,bottom=0.1,top=0.95,left=0.10,right=0.98)
ax = [fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[0,2]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1]),fig.add_subplot(gs[1,2]),fig.add_subplot(gs[2,0]),fig.add_subplot(gs[2,1]),fig.add_subplot(gs[2,2])]

d = Dataset(reccap_file,'r')
reccap = np.array(d['reccap_filled'])
d.close()

c = Dataset(output_file,'a')
socat_fco2 = np.array(c['fco2_ave_weighted'])
socat_fco2_recalc = np.array(c['fco2_recalculated_ave_weighted'])
keys = list(c.variables.keys())

reccap = np.repeat(reccap[:, :, np.newaxis], socat_fco2.shape[2], axis=2)
unique = np.unique(reccap)
print(unique)

matching = [s for s in keys if "sfco2" in s]
print(matching)
t = 0
lim = np.array([0,1000])
for va in matching:
    print(va)
    if any(p in va for p in recalculated_socat_prod):
        print('Recalculated fCO2 product')
        socat = socat_fco2_recalc
        label = 'in situ recalculated fCO$_{2 (sw)}$ ($\mu$atm)'
        col = 'r'
    else:
        print('Orginial fCO2 product')
        socat = socat_fco2
        label = 'in situ fCO$_{2 (sw)}$ ($\mu$atm)'
        col = 'b'
    if any(p in va for p in cool_skin_prod):
        print('Cool skin product')
        s = va.split('_')
        data = np.array(c[va])
        fco2_atm = np.array(c[s[0]+'_fco2atm'])
        alpha = np.array(c[s[0]+'_alpha'])
        alpha_skin = np.array(c[s[0]+'_alpha_skin'])
        ax[t].scatter(socat,data,c=col)
        nnt.unweight(socat.ravel(),data.ravel(),ax[t],lim)
        stats_un = ws.unweighted_stats(socat.ravel(),data.ravel(),va)
        print(stats_un)
        ax[t].plot(lim,lim,'k-')
        ax[t].plot(lim,lim*stats_un['slope'] + stats_un['intercept'],'k--')
        ax[t].set_title(va)
        ax[t].set_xlabel(label)
        ax[t].set_ylabel('Predicted fCO$_{2 (sw)}$ ($\mu$atm)')
        rmsd_unc = np.zeros((data.shape)); rmsd_unc[:] = np.nan
        for i in unique:
            f = np.where(reccap == i)
            stats_un = ws.unweighted_stats(socat[f].ravel(),data[f].ravel(),va)
            print(stats_un['rmsd'])
            rmsd_unc[f] = stats_un['rmsd']*2
        l = np.where(np.isnan(data)==1)
        rmsd_unc[l] = np.nan
        conc = (alpha*data)
        data = (rmsd_unc / np.abs(data)) * conc
        data = data/ np.abs(conc - (fco2_atm*alpha_skin))

        data[np.isinf(data) == 1] = 10000
        data[data > 10000] = 10000
    else:
        print('Non cool skin product')
        s = va.split('_')
        data = np.array(c[va])
        fco2_atm = np.array(c[s[0]+'_fco2atm']) # Temp replace of fco2atm so I can run results...
        # fco2_atm = np.array(c['UExP-FNN-U-v2_fco2atm'])
        ax[t].scatter(socat,data,c=col)
        nnt.unweight(socat.ravel(),data.ravel(),ax[t],lim)
        stats_un = ws.unweighted_stats(socat.ravel(),data.ravel(),va)
        print(stats_un)
        ax[t].plot(lim,lim,'k-')
        ax[t].plot(lim,lim*stats_un['slope'] + stats_un['intercept'],'k--')
        ax[t].set_title(va)
        ax[t].set_xlabel(label)
        ax[t].set_ylabel('Predicted fCO$_{2 (sw)}$ ($\mu$atm)')
        rmsd_unc = np.zeros((data.shape)); rmsd_unc[:] = np.nan
        for i in unique:
            f = np.where(reccap == i)
            stats_un = ws.unweighted_stats(socat[f].ravel(),data[f].ravel(),va)
            print(stats_un['rmsd'])
            rmsd_unc[f] = stats_un['rmsd']*2
        l = np.where(np.isnan(data)==1)
        rmsd_unc[l] = np.nan
        data = rmsd_unc / np.abs(data - fco2_atm)
        data[np.isinf(data) == 1] = 10000
        data[data > 10000] = 10000
    ax[t].set_xlim(lim)
    ax[t].set_ylim(lim)
    if s[0]+'_rmsd_unc' in keys:
        c[s[0]+'_rmsd_unc'][:] = rmsd_unc
    else:
        var = c.createVariable(s[0]+'_rmsd_unc',np.float32,('lon','lat','time'))
        var[:] = rmsd_unc

    if s[0]+'_unc' in keys:
        c[s[0]+'_unc'][:] = data
    else:
        var = c.createVariable(s[0]+'_unc',np.float32,('lon','lat','time'))
        var[:] = data
    t=t+1

if 'ice' in keys:
    c['ice'] = np.zeros((data.shape))
else:
    var = c.createVariable('ice',np.float32,('lon','lat','time'))
    var[:] = np.zeros((data.shape))
fig.savefig(os.path.join(working_directory,'plots','validation.png'),format='png',dpi=300)
c.close()
