#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 06/2024

"""
cols = ['#332288','#44AA99','#882255','#DDCC77', '#117733', '#88CCEE','#999933','#CC6677']
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
from matplotlib.gridspec import GridSpec

model_gcb = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/GCB_model_fluxes.csv'

model_loc = 'E:/SOCOMV2/EX2/flux/models'
years_lims = [1970,2022]
data = pd.read_table(model_gcb,sep=',')

#print(data)
head = list(data); head.remove('year')
#print(head)

# plt.figure(figsize=(7,7))
# co = 0
# for t in head:
#     plt.plot(data['year'],data[t],label=t,color=cols[co])
#     model_f = os.path.join(model_loc,t,t+'_full.csv')
#     data2 = pd.read_table(model_f,sep=',')
#     plt.plot(data2['# Year'],-data2[' Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--',label=t+' (product)')
#     co = co+1
#
# plt.ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
# plt.xlabel('Year')
# plt.title('SOCOMv2 Ex2 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
# plt.grid()
# plt.legend()
# plt.savefig('plots/SOCOMv2_model_flux_comparision.png',format='png',dpi=300)
#
#
# fig = plt.figure(figsize=(10,7))
# gs = GridSpec(1,1, figure=fig, wspace=0.25,hspace=0.15,bottom=0.1,top=0.95,left=0.1,right=0.72)
# ax = fig.add_subplot(gs[0,0])
# co = 0
# for t in head:
#     model_f = os.path.join(model_loc,t,t+'_full.csv')
#     data2 = pd.read_table(model_f,sep=',')
#     plt.plot(data2['# Year'],-data2['Downward air-sea CO2 flux (Pg C yr-1)'],color=cols[co],label=t+' (ingas)')
#     plt.plot(data2['# Year'],-data2['Upward air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--',label=t+' (outgas)')
#     co = co+1
#
# plt.ylabel('Air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
# plt.xlabel('Year')
# plt.title('SOCCOMv2 Ex2 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
# plt.grid()
# plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)
# plt.savefig('plots/SOCOMv2_model_flux_comparision_inVSout.png',format='png',dpi=300)

output_loc = 'E:/SOCOMV2/EX2/flux/final_output'
mod_dictionary = {'FESOM': 'FESOM2_REcoM',
    'CESM': 'CESM_ETHZ_r1',
    'IPSL': 'IPSL_r1',
    'MRI': 'MRI_ESM2_2'}

    #'NorESM': 'NorESM_OC1_2'}
mod_keys = list(mod_dictionary.keys())
fig = plt.figure(figsize=(14,14))
gs = GridSpec(2,2, figure=fig, wspace=0.25,hspace=0.25,bottom=0.1,top=0.95,left=0.1,right=0.9)
plt.suptitle('SOCOMv2 Ex2 Scaled - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
fig2 = plt.figure(figsize=(14,14))
gs = GridSpec(2,2, figure=fig2, wspace=0.25,hspace=0.25,bottom=0.1,top=0.95,left=0.1,right=0.9)
plt.suptitle('SOCOMv2 Ex2 Scaled - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
ax = [fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1])]
ax2 = [fig2.add_subplot(gs[0,0]),fig2.add_subplot(gs[0,1]),fig2.add_subplot(gs[1,0]),fig2.add_subplot(gs[1,1])]


t = 0
for i in range(len(mod_keys)):
    data = pd.read_table(os.path.join(output_loc,mod_keys[i]+'_full.csv'),sep=',')

    data_keys = list(data)
    data[data==0] = np.nan
    prod = []
    for h in data_keys:
        if 'Net_AirSea' in h:
            prod.append(h.split('_')[0])
    print(prod)
    if t == 0:
        data_cols = {}
        for h in range(len(prod)):
            data_cols[prod[h]] = cols[h]
        print(data_cols)
        t=1

    #p = 0
    for j in prod:
        if j == 'Model':
            ax[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=data_cols[j],linewidth=3,label='Model Truth')
            ax2[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=cols[0],linewidth=3,label='Model Truth')
        else:
            cover = np.nanmean(data[j+'_Global_IceFree_Area_Flux (m-2)'] / data['Model_Global_IceFree_Area_Flux (m-2)'])
            print(cover)
            if cover < 0.99:
                ax[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'] * (1/cover),color=data_cols[j],label=j +' Scaled (area covered = '+str(round(cover*100,2))+'%)')
                ax2[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'] * (1/cover),color=cols[1])
            else:
                ax[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=data_cols[j],label=j + ' Not scaled (area covered = '+str(round(cover*100,2))+'%)')
                ax2[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=cols[1])

    ax[i].set_title(mod_dictionary[mod_keys[i]])
    ax[i].legend(fontsize=9)
    ax[i].set_xlabel('Year')
    ax[i].set_ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
    ax[i].grid()
    ax[i].set_ylim([0,4])
    ax[i].set_xlim(years_lims)

    ax2[i].set_title(mod_dictionary[mod_keys[i]])
    ax2[i].set_xlabel('Year')
    ax2[i].set_ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
    ax2[i].grid()
    ax2[i].set_ylim([0,4])
    ax2[i].set_xlim(years_lims)

fig.savefig('plots/SOCOMv2_data_product_model_comparision_nothidden.png',format='png',dpi=300)
fig2.savefig('plots/SOCOMv2_data_product_model_comparision_hidden.png',format='png',dpi=300)


output_loc = 'E:/SOCOMV2/EX2/flux/final_output'
mod_dictionary = {'FESOM': 'FESOM2_REcoM',
    'CESM': 'CESM_ETHZ_r1',
    'IPSL': 'IPSL_r1',
    'MRI': 'MRI_ESM2_2'}

    #'NorESM': 'NorESM_OC1_2'}
mod_keys = list(mod_dictionary.keys())
fig = plt.figure(figsize=(14,14))
gs = GridSpec(2,2, figure=fig, wspace=0.25,hspace=0.25,bottom=0.1,top=0.95,left=0.1,right=0.9)
plt.suptitle('SOCOMv2 Ex2 Consistent - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
fig2 = plt.figure(figsize=(14,14))
gs = GridSpec(2,2, figure=fig2, wspace=0.25,hspace=0.25,bottom=0.1,top=0.95,left=0.1,right=0.9)
plt.suptitle('SOCOMv2 Ex2 Consistent - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
ax = [fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[1,0]),fig.add_subplot(gs[1,1])]
ax2 = [fig2.add_subplot(gs[0,0]),fig2.add_subplot(gs[0,1]),fig2.add_subplot(gs[1,0]),fig2.add_subplot(gs[1,1])]


t = 0
for i in range(len(mod_keys)):
    data = pd.read_table(os.path.join(output_loc,mod_keys[i]+'_consistent.csv'),sep=',')
    data_keys = list(data)
    data[data==0] = np.nan
    prod = []
    for h in data_keys:
        if 'Net_AirSea' in h:
            prod.append(h.split('_')[0])
    print(prod)
    if t == 0:
        data_cols = {}
        for h in range(len(prod)):
            data_cols[prod[h]] = cols[h]
        print(data_cols)
        t=1

    #p = 0
    for j in prod:
        if j == 'Model':
            ax[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=data_cols[j],linewidth=3,label='Model Truth')
            ax2[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=cols[0],linewidth=3,label='Model Truth')
        else:
            cover = np.nanmean(data[j+'_Global_IceFree_Area_Flux (m-2)'] / data['Model_Global_IceFree_Area_Flux (m-2)'])
            print(cover)
            if cover < 0.99:
                ax[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'] * (1/cover),color=data_cols[j],label=j +' Scaled (area covered = '+str(round(cover*100,2))+'%)')
                ax2[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'] * (1/cover),color=cols[1])
            else:
                ax[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=data_cols[j],label=j + ' Not scaled (area covered = '+str(round(cover*100,2))+'%)')
                ax2[i].plot(data['# Year'],-data[j+'_Net_AirSea_Flux (PgCyr-1)'],color=cols[1])

    ax[i].set_title(mod_dictionary[mod_keys[i]])
    ax[i].legend(fontsize=9)
    ax[i].set_xlabel('Year')
    ax[i].set_ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
    ax[i].grid()
    ax[i].set_ylim([0,4])
    ax[i].set_xlim(years_lims)

    ax2[i].set_title(mod_dictionary[mod_keys[i]])
    ax2[i].set_xlabel('Year')
    ax2[i].set_ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
    ax2[i].grid()
    ax2[i].set_ylim([0,4])
    ax2[i].set_xlim(years_lims)

fig.savefig('plots/SOCOMv2_data_product_model_comparision_nothidden_consistent.png',format='png',dpi=300)
fig2.savefig('plots/SOCOMv2_data_product_model_comparision_hidden_consistent.png',format='png',dpi=300)
