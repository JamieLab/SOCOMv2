#!/usr/bin/env python3
import numpy as np
import datetime
from netCDF4 import Dataset
import numpy as np
import glob
import os
import sys
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt

oceanicu_frame = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'

sys.path.append(os.path.join(oceanicu_frame))
sys.path.append(os.path.join(oceanicu_frame,'Data_Loading'))

import fluxengine_driver as fl

input_file = 'output.nc'
model_save_loc = ''

c = Dataset(input_file,'r')
keys = list(c.variables.keys())

c.close()
matching = [s for s in keys if "sfco2" in s]
#matching = ['Jena-MLS_sfco2']
for v in matching:
    s = v.split('_')
    if v == 'UExP-FNN-U-v2_sfco2':
        fl.variogram_evaluation(model_save_loc,input_array = ['fco2_reanalysed_ave_weighted',v],input_datafile=[input_file,input_file], start_yr=1990,end_yr=2023,output_file=s[0])
    else:
        fl.variogram_evaluation(model_save_loc,input_array = ['fco2_ave_weighted',v],input_datafile=[input_file,input_file], start_yr=1990,end_yr=2023,output_file=s[0])

for v in matching:
    s = v.split('_')
    fl.montecarlo_flux_testing(model_save_loc='D:/ESA_CONTRACT/NN/GCB_TESTING',
        start_yr = 1990,
        end_yr = 2022,
        decor='decorrelation/'+s[0]+'.csv',
        flux_var = s[0]+'_unc',
        flux_variable = s[0]+'_fgco2',
        inp_file = input_file,
        single_output = s[0],
        ens=100)

g = glob.glob('*.csv')
fig = plt.figure(figsize=(7,7))
gs = GridSpec(1,1, figure=fig, wspace=0.5,hspace=0.2,bottom=0.1,top=0.95,left=0.15,right=0.98)
ax = fig.add_subplot(gs[0,0])
a = list(range(1990,2022+1))
col = ['tab:blue','tab:orange','tab:green','tab:purple','tab:red','tab:brown','tab:pink','tab:cyan']
co = 0
data = np.zeros((len(a),len(g),2))
data[:] =np.nan
data2 = np.copy(data)
#print(g)
for i in g:
    print(i)
    la = i.split('\\')
    print(la[-1].split('.')[0] )
    ann = np.loadtxt(i,delimiter=',',skiprows=1)

    if la[-1].split('.')[0] == 'UoEX':
        print('UoEx')
        ann[:,1:3] = ann[:,1:3] * (1/0.9761)
        ann[:,2] = ann[:,2]+0.65
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='--')
    elif la[-1].split('.')[0] == 'NIES-ML3':
        ann[:,1:3] = ann[:,1:3] * (1/0.9530)
        ann[:,2] = ann[:,2]+0.65
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0] == 'CMEMS-LSCE-FFNN':
        ann[:,1:3] = ann[:,1:3] * (1/0.9444)
        ann[:,2] = ann[:,2]+0.65
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    else:
        ann[:,2] = ann[:,2]+0.65
        # data[:,co,0] = ann[:,2]
        # data[:,co,1] = ann[:,1]
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0])

    ax.fill_between(a,ann[:,2] - ann[:,1],ann[:,2] + ann[:,1],alpha = 0.6,zorder=5,color = col[co])
    if la[-1].split('.')[0] != 'UExP-FNN-U-v2':
        data[:,co,0] = ann[:,2]
        data[:,co,1] = ann[:,1]
    #ax.fill_between(a,ann[:,0] - (2*ann[:,1]),ann[:,0] + (2*ann[:,1]),alpha=0.4,color='k',zorder=4)
    data2[:,co,0] = ann[:,2]
    data2[:,co,1] = ann[:,1]
    co = co+1

m_data = np.nanmean(data[:,:,0],axis=1)
m_data_unc = np.nanmean(data[:,:,1],axis=1)
print(m_data)
print(m_data_unc)
ax.plot(a,m_data,zorder=7,linewidth=3,color='k',label='Mean without UoEx')
ax.fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k')
m_data = np.nanmean(data2[:,:,0],axis=1)
m_data_unc = np.nanmean(data2[:,:,1],axis=1)
ax.plot(a,m_data,zorder=7,linewidth=3,color='k',linestyle ='--',label='Mean with UoEx')
#ax.fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k')
ax.set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
ax.set_xlabel('Year')
ax.set_ylim([0,5])

ann = np.loadtxt('gcbmodels\gcb_models.csv',delimiter=',',skiprows=1)
ax.plot(ann[:,0],ann[:,1],'b-',zorder=7,linewidth=3,label='GCB Model Mean')
ax.legend(fontsize=11)

fig.savefig('plots/1sigma_uncertainty.png',format='png',dpi=300)

fig = plt.figure(figsize=(7,7))
gs = GridSpec(1,1, figure=fig, wspace=0.5,hspace=0.2,bottom=0.1,top=0.95,left=0.15,right=0.98)
ax = fig.add_subplot(gs[0,0])
a = list(range(1990,2022+1))
#col = ['tab:blue','tab:orange','tab:green','tab:purple','tab:red','tab:brown','tab:pink','tab:gray','tab:cyan']
co = 0
data = np.zeros((len(a),len(g),2))
data[:] =np.nan
data2 = np.copy(data)
#print(g)
for i in g:
    print(i)
    la = i.split('\\')
    print(la[-1].split('.')[0] )
    ann = np.loadtxt(i,delimiter=',',skiprows=1)

    if la[-1].split('.')[0] == 'UoEX':
        print('UoEx')
        ann[:,1:3] = ann[:,1:3] * (1/0.9761)
        ann[:,2] = ann[:,2]+0.65
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='--')
    elif la[-1].split('.')[0] == 'NIES-ML3':
        ann[:,1:3] = ann[:,1:3] * (1/0.9530)
        ann[:,2] = ann[:,2]+0.65
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0] == 'CMEMS-LSCE-FFNN':
        ann[:,1:3] = ann[:,1:3] * (1/0.9444)
        ann[:,2] = ann[:,2]+0.65
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    else:

        ann[:,2] = ann[:,2]+0.65
        ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0])
    if la[-1].split('.')[0] != 'UExP-FNN-U-v2':
        data[:,co,0] = ann[:,2]
        data[:,co,1] = ann[:,1]*2
    ax.fill_between(a,ann[:,2] - ann[:,1]*2,ann[:,2] + ann[:,1]*2,alpha = 0.6,zorder=5,color = col[co])
    data2[:,co,0] = ann[:,2]
    data2[:,co,1] = ann[:,1]*2
    #ax.fill_between(a,ann[:,0] - (2*ann[:,1]),ann[:,0] + (2*ann[:,1]),alpha=0.4,color='k',zorder=4)
    co = co+1

m_data = np.nanmean(data[:,:,0],axis=1)
m_data_unc = np.nanmean(data[:,:,1],axis=1)
# print(m_data)
# print(m_data_unc)
ax.plot(a,m_data,zorder=7,linewidth=3,color='k',label='Mean without UoEx')
ax.fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k')
m_data = np.nanmean(data2[:,:,0],axis=1)
m_data_unc = np.nanmean(data2[:,:,1],axis=1)
ax.plot(a,m_data,zorder=7,linewidth=3,color='k',linestyle ='--',label='Mean with UoEx')
#ax.fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k')
ax.set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
ax.set_xlabel('Year')
ax.set_ylim([0,5])

ann = np.loadtxt('gcbmodels\gcb_models.csv',delimiter=',',skiprows=1)
ax.plot(ann[:,0],ann[:,1],'b-',zorder=7,linewidth=3,label='GCB Model Mean')
ax.legend(fontsize=11)

fig.savefig('plots/2sigma_uncertainty.png',format='png',dpi=300)
