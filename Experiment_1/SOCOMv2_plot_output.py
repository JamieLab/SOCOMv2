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

working_directory = 'D:/SOCOMv2/Experiment1/GCB2025'
g = glob.glob(os.path.join(working_directory,'*.csv'))
fig,ax = plt.subplots(2,2,figsize=(14,14))
fig.suptitle('SOCOMv2 Experiment 1 - '+ datetime.datetime.now().strftime('%d-%m-%Y %H:%M'))
ax = ax.ravel()
a = list(range(1990,2024+1))
# col = ['tab:blue','tab:orange','tab:green','tab:purple','tab:red','tab:brown','tab:pink','tab:cyan','tab:olive']
col = ['#332288','#44AA99','#882255','#DDCC77', '#117733', '#88CCEE','#999933','#CC6677','tab:olive']
co = 0
data = np.zeros((len(a),len(g),2))
data[:] =np.nan
data2 = np.copy(data)
#print(g)
col_dir = {}
for i in g:
    la = i.split('\\')
    col_dir[la[-1].split('.')[0] ] = col[co]
    co=co+1

co = 0
for i in g:
    print(i)
    la = i.split('\\')
    print(la[-1].split('.')[0] )
    ann = np.loadtxt(i,delimiter=',',skiprows=1)
    if np.all(np.sign(ann[:,2])==-1):
        ann[:,2] = -1*ann[:,2]

    if la[-1].split('.')[0] == 'LDEO-HPD':
        print('LDEO')
        ann[:,1:3] = ann[:,1:3] * (1/0.9351)
        ann[:,2] = ann[:,2]+0.65
        ax[0].plot(a,ann[:,2],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0]],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0] == 'NIES-ML3':
        ann[:,1:3] = ann[:,1:3] * (1/0.9491)
        ann[:,2] = ann[:,2]+0.65
        ax[0].plot(a,ann[:,2],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0]],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0] == 'CMEMS-LSCE-FFNN':
        ann[:,1:3] = ann[:,1:3] * (1/0.9444)
        ann[:,2] = ann[:,2]+0.65
        ax[0].plot(a,ann[:,2],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0]],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0] == 'CSIR-ML6':
        ann[:,1:3] = ann[:,1:3] * (1/0.9619)
        ann[:,2] = ann[:,2]+0.65
        ax[0].plot(a,ann[:,2],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0]],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
    else:
        ann[:,2] = ann[:,2]+0.65
        # data[:,co,0] = ann[:,2]
        # data[:,co,1] = ann[:,1]
        ax[0].plot(a,ann[:,2],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0]],label=la[-1].split('.')[0])

    ax[0].fill_between(a,ann[:,2] - ann[:,1],ann[:,2] + ann[:,1],alpha = 0.6,zorder=5,color = col_dir[la[-1].split('.')[0]])
    # if la[-1].split('.')[0] != 'UExP-FNN-U':
    #     data[:,co,0] = ann[:,2]
    #     data[:,co,1] = ann[:,1]
    #ax.fill_between(a,ann[:,0] - (2*ann[:,1]),ann[:,0] + (2*ann[:,1]),alpha=0.4,color='k',zorder=4)
    data2[:,co,0] = ann[:,2]
    data2[:,co,1] = ann[:,1]
    co = co+1
ax[0].set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
ax[0].set_xlabel('Year')
ax[0].set_ylim([1,5])
ax[0].grid()
ax[0].legend(fontsize=10)


m_data = np.nanmean(data2[:,:,0],axis=1)
m_data_unc = np.nanmean(data2[:,:,1],axis=1)
m_data2_unc = np.sqrt(np.nansum(data2[:,:,1]**2,axis=1))/8
print(m_data)
print(m_data_unc)
ax[1].plot(a,m_data,zorder=7,linewidth=3,color='k',linestyle ='--',label='Mean')
ax[1].fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k',label='Correlated uncertainty (1 sigma)')
ax[1].fill_between(a,m_data - m_data2_unc,m_data + m_data2_unc,alpha = 0.6,zorder=5,color = 'r',label='Independent uncertainty (1 sigma)')
ax[1].fill_between(a,m_data - (m_data2_unc*2),m_data + (m_data2_unc*2),alpha = 0.4,zorder=5,color = 'r',label='Independent uncertainty (2 sigma)')
ax[1].set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
ax[1].set_xlabel('Year')
ax[1].set_ylim([1,5])
ax[1].grid()
ax[1].legend(fontsize=10)

dd3 = np.copy(m_data_unc)
dd = np.copy(m_data2_unc)
print(np.mean(dd3))
print(np.mean(dd))

g = glob.glob(os.path.join(working_directory,'flux','*.csv'))
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
    if np.all(np.sign(ann[:,1])==-1):
        ann[:,1] = -1*ann[:,1]
    ann[:,2:4] = np.abs(ann[:,2:4])

    if la[-1].split('.')[0].split('_')[0] == 'LDEO-HPD':
        print('LDEO')
        ann[:,1] = ann[:,1] * (1/0.9351)
        ann[:,1] = ann[:,1]+0.65
        ap = np.sum(ann[:,2:4],axis=1) * 0.1 * (1/0.9351)
        ax[2].plot(a,ann[:,1],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0].split('_')[0]],label=la[-1].split('.')[0].split('_')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0].split('_')[0] == 'NIES-ML3':
        ann[:,1] = ann[:,1] * (1/0.9491)
        ann[:,1] = ann[:,1]+0.65
        ap = np.sum(ann[:,2:4],axis=1) * 0.1 * (1/0.9491)
        ax[2].plot(a,ann[:,1],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0].split('_')[0]],label=la[-1].split('.')[0].split('_')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0].split('_')[0] == 'CMEMS-LSCE-FFNN':
        ann[:,1] = ann[:,1] * (1/0.9444)
        ann[:,1] = ann[:,1]+0.65
        ap = np.sum(ann[:,2:4],axis=1) * 0.1 * (1/0.9444)
        ax[2].plot(a,ann[:,1],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0].split('_')[0]],label=la[-1].split('.')[0].split('_')[0]+ ' (scaled)',linestyle='-')
    elif la[-1].split('.')[0].split('_')[0] == 'CSIR-ML6':
        ann[:,1:4] = ann[:,1:4] * (1/0.9619)
        ann[:,1] = ann[:,1]+0.65
        ap = np.sum(ann[:,2:4],axis=1) * 0.1 * (1/0.9619)
        ax[2].plot(a,ann[:,1],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0].split('_')[0]],label=la[-1].split('.')[0].split('_')[0]+ ' (scaled)',linestyle='-')
    else:
        ann[:,1] = ann[:,1]+0.65
        # data[:,co,0] = ann[:,2]
        # data[:,co,1] = ann[:,1]
        ax[2].plot(a,ann[:,1],zorder=6,linewidth=3,color=col_dir[la[-1].split('.')[0].split('_')[0]],label=la[-1].split('.')[0].split('_')[0])
        ap = np.sum(ann[:,2:4],axis=1) * 0.1
    ax[2].fill_between(a,ann[:,1] - ap,ann[:,1] + ap,alpha = 0.6,zorder=5,color = col_dir[la[-1].split('.')[0].split('_')[0]])
    # if la[-1].split('.')[0] != 'UExP-FNN-U':
    #     data[:,co,0] = ann[:,2]
    #     data[:,co,1] = ann[:,1]
    #ax.fill_between(a,ann[:,0] - (2*ann[:,1]),ann[:,0] + (2*ann[:,1]),alpha=0.4,color='k',zorder=4)
    data2[:,co,0] = ann[:,1]
    data2[:,co,1] = ap
    co = co+1
ax[2].set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
ax[2].set_xlabel('Year')
ax[2].set_ylim([1,5])
ax[2].grid()
ax[2].legend(fontsize=10)

m_data = np.nanmean(data2[:,:,0],axis=1)
m_data_unc = np.nanmean(data2[:,:,1],axis=1)
dd2 = np.copy(m_data_unc)
print(np.mean(dd2))
# print(m_data)
# print(m_data_unc)
ax[3].plot(a,m_data,zorder=7,linewidth=3,color='k',linestyle ='--',label='Mean')
ax[3].fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k',label='Correlated uncertainty (1 sigma)')
# ax[1].fill_between(a,m_data - m_data2_unc,m_data + m_data2_unc,alpha = 0.6,zorder=5,color = 'r',label='Independent uncertainty')
# ax[1].fill_between(a,m_data - (m_data2_unc*2),m_data + (m_data2_unc*2),alpha = 0.4,zorder=5,color = 'r',label='Independent uncertainty (2 sigma)')
ax[3].set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
ax[3].set_xlabel('Year')
ax[3].set_ylim([1,5])
ax[3].grid()
ax[3].legend(fontsize=10)

for i in [0,1]:
    ax[i].set_title('fCO2sw component')
for i in [2,3]:
    ax[i].set_title('Gas transfer velocity')
plt.tight_layout()


fig.savefig(os.path.join(working_directory,'plots/SOCOMv2_Experiment_1_1sigma_uncertainty_component.png'),format='png',dpi=300)

fig,ax = plt.subplots(1,1,figsize=(7,7))
fig.suptitle('SOCOMv2 Experiment 1 - '+ datetime.datetime.now().strftime('%d-%m-%Y %H:%M'))
unc = np.sqrt(dd**2 + dd2**2)
unc2 = np.sqrt(dd3**2 + dd2**2)
print(np.mean(unc))
print(np.mean(unc2))

ax.plot(a,m_data,'k')
ax.fill_between(a,m_data - unc,m_data + unc,alpha = 0.6,zorder=5,color = 'r',label='Uncertainty independent (1 sigma)')
ax.fill_between(a,m_data - unc2,m_data + unc2,alpha = 0.6,zorder=5,color = 'k',label='Uncertainty correlated (1 sigma)')
ax.set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
ax.set_xlabel('Year')
ax.set_ylim([1,5])
ax.grid()
ax.legend(fontsize=10)
fig.savefig(os.path.join(working_directory,'plots/SOCOMv2_Experiment_1_1sigma_uncertainty.png'),format='png',dpi=300)
# fig = plt.figure(figsize=(7,7))
# gs = GridSpec(1,1, figure=fig, wspace=0.5,hspace=0.2,bottom=0.1,top=0.95,left=0.15,right=0.98)
# ax = fig.add_subplot(gs[0,0])
# #a = list(range(1990,2022+1))
# #col = ['tab:blue','tab:orange','tab:green','tab:purple','tab:red','tab:brown','tab:pink','tab:gray','tab:cyan']
# co = 0
# data = np.zeros((len(a),len(g),2))
# data[:] =np.nan
# data2 = np.copy(data)
# #print(g)
# for i in g:
#     print(i)
#     la = i.split('\\')
#     print(la[-1].split('.')[0] )
#     ann = np.loadtxt(i,delimiter=',',skiprows=1)
#
#     if la[-1].split('.')[0] == 'LDEO-HPD':
#         print('LDEO')
#         ann[:,1:3] = ann[:,1:3] * (1/0.9351)
#         ann[:,2] = ann[:,2]+0.65
#         ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
#     elif la[-1].split('.')[0] == 'NIES-ML3':
#         ann[:,1:3] = ann[:,1:3] * (1/0.9491)
#         ann[:,2] = ann[:,2]+0.65
#         ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
#     elif la[-1].split('.')[0] == 'CMEMS-LSCE-FFNN':
#         ann[:,1:3] = ann[:,1:3] * (1/0.9444)
#         ann[:,2] = ann[:,2]+0.65
#         ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
#     elif la[-1].split('.')[0] == 'CSIR-ML6':
#         ann[:,1:3] = ann[:,1:3] * (1/0.9619)
#         ann[:,2] = ann[:,2]+0.65
#         ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0]+ ' (scaled)',linestyle='-')
#     else:
#
#         ann[:,2] = ann[:,2]+0.65
#         ax.plot(a,ann[:,2],zorder=6,linewidth=3,color=col[co],label=la[-1].split('.')[0])
#     if la[-1].split('.')[0] != 'UExP-FNN-U-v2':
#         data[:,co,0] = ann[:,2]
#         data[:,co,1] = ann[:,1]*2
#     ax.fill_between(a,ann[:,2] - ann[:,1]*2,ann[:,2] + ann[:,1]*2,alpha = 0.6,zorder=5,color = col[co])
#     data2[:,co,0] = ann[:,2]
#     data2[:,co,1] = ann[:,1]*2
#     #ax.fill_between(a,ann[:,0] - (2*ann[:,1]),ann[:,0] + (2*ann[:,1]),alpha=0.4,color='k',zorder=4)
#     co = co+1
#
# m_data = np.nanmean(data[:,:,0],axis=1)
# m_data_unc = np.nanmean(data[:,:,1],axis=1)
# # print(m_data)
# # print(m_data_unc)
# ax.plot(a,m_data,zorder=7,linewidth=3,color='k',label='Mean without UoEx')
# ax.fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k')
# m_data = np.nanmean(data2[:,:,0],axis=1)
# m_data_unc = np.nanmean(data2[:,:,1],axis=1)
# ax.plot(a,m_data,zorder=7,linewidth=3,color='k',linestyle ='--',label='Mean with UoEx')
# #ax.fill_between(a,m_data - m_data_unc,m_data + m_data_unc,alpha = 0.6,zorder=5,color = 'k')
# ax.set_ylabel('Net air-sea CO$_{2}$ flux + riverine (Pg C yr$^{-1}$)')
# ax.set_xlabel('Year')
# ax.set_ylim([0,5])
#
# ann = np.loadtxt('gcbmodels\gcb_models.csv',delimiter=',',skiprows=1)
# ax.plot(ann[:,0],ann[:,1],'b-',zorder=7,linewidth=3,label='GCB Model Mean')
# ax.legend(fontsize=11)
#
# fig.savefig('plots/2sigma_uncertainty.png',format='png',dpi=300)
