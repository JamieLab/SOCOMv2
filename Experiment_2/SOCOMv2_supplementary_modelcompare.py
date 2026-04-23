#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 17/01/2025

"""
cols = ['#332288','#44AA99','#882255', '#117733', '#88CCEE','#999933','#CC6677','#AA4499'] # '#DDCC77' IPSL colour

import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats
oceanicu_loc = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(oceanicu_loc)
sys.path.append(os.path.join(oceanicu_loc,'Data_Loading'))
import data_utils as du

flux_location = 'E:/SOCOMV2/EX2/flux/'
model_location = os.path.join(flux_location,'models')

import matplotlib.transforms
font = {'weight' : 'normal',
        'size'   :10}
matplotlib.rc('font', **font)

plot_ylim = [-3.5,-0.5]


model_gcb = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/SOCOMv2/EX2/GCB_model_fluxes.csv'
data = pd.read_table(model_gcb,sep=','); head = list(data); head.remove('year'); head.remove('IPSL_r1')
fig,ax = plt.subplots(1,3,figsize=(18,6))
ax = ax.ravel()
co = 0
for t in head:
    stat = scipy.stats.linregress(data['year'],data[t])
    print(stat)
    # ax[0].plot(data['year'],data[t],label=t+' (GCB2023) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$)',color=cols[co])
    ax[0].plot(data['year'],-data[t],label=t+'',color=cols[co])
    model_f = os.path.join(model_location,t,t+'_full_model_k.csv')
    data2 = pd.read_table(model_f,sep=',')
    stat = scipy.stats.linregress(data2['# Year'],data2['Net air-sea CO2 flux (Pg C yr-1)'])
    # ax[0].plot(data2['# Year'],-data2['Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--',label=t+' (SOCOMv2) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$)')
    ax[0].plot(data2['# Year'],data2['Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--')

    co = co+1

ax[0].set_ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; -ve into ocean)')
ax[0].set_xlabel('Year')
# plt.title('SOCOMv2 Ex2 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
ax[0].set_ylim(plot_ylim)
ax[0].set_xlim([1970,2022])
ax[0].grid()
ax[0].legend()


model_loc = 'E:/SOCOMV2/EX2/flux/models'
a_scale = [0.251,0.251,0.310,0.337,0.251]
years_lims = [1970,2022]
data = pd.read_table(model_gcb,sep=',')

#print(data)
head = list(data); head.remove('year')
#print(head)

# plt.figure(figsize=(10,10))
co = 0
for t in head:
    stat = scipy.stats.linregress(data['year'],data[t])
    print(stat)
    # ax[1].plot(data['year'],data[t],label=t+' (GCB2023) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$)',color=cols[co])
    ax[1].plot(data['year'],-data[t],label=t+' (c = '+str(a_scale[co])+')',color=cols[co])
    model_f = os.path.join(model_loc,t,t+f'_full_a{int(a_scale[co]*1000)}.csv')
    data2 = pd.read_table(model_f,sep=',')
    stat = scipy.stats.linregress(data2['# Year'],data2['Net air-sea CO2 flux (Pg C yr-1)'])
    # ax[1].plot(data2['# Year'],-data2['Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--',label=t+' (SOCOMv2) ('+str(round(stat.slope*10,2))+' Pg C dec$^{-1}$) - ' + f'a = {a_scale[co]}')
    ax[1].plot(data2['# Year'],data2['Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--')
    co = co+1

# plt.ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
ax[1].set_xlabel('Year')
# plt.title('SOCOMv2 Ex2 Model a scaling - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
ax[1].set_ylim(plot_ylim)
ax[1].set_xlim([1970,2022])
ax[1].grid()
ax[1].legend()


years_lims = [1970,2022]
data = pd.read_table(model_gcb,sep=',')

#print(data)
head = list(data); head.remove('year')
#print(head)

co = 0
for t in head:
    stat = scipy.stats.linregress(data['year'],-data[t])
    print(stat)
    ax[2].plot(data['year'],-data[t],label=t+'',color=cols[co])
    model_f = os.path.join(model_loc,t,t+'_full.csv')
    data2 = pd.read_table(model_f,sep=',')
    stat = scipy.stats.linregress(data2['# Year'],data2['Net air-sea CO2 flux (Pg C yr-1)'])
    ax[2].plot(data2['# Year'],data2['Net air-sea CO2 flux (Pg C yr-1)'],color=cols[co],linestyle='--')
    co = co+1

# plt.ylabel('Net air-sea CO$_2$ flux (Pg C yr$^{-1}$; +ve into ocean)')
ax[2].set_xlabel('Year')
# plt.title('SOCOMv2 Ex2 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
ax[2].set_ylim(plot_ylim)
ax[2].set_xlim([1970,2022])
ax[2].grid()
ax[2].legend()

let = ['a','b','c']
for i in range(3):
    ax[i].text(0.93,1.05,f'({let[i]})',transform=ax[i].transAxes,va='top',fontweight='bold',fontsize = 18)
plt.tight_layout()
plt.savefig('plots/SOCOMv2_supplmentary.png',format='png',dpi=300)
