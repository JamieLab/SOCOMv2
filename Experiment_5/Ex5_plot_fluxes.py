#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 05/2025

"""
cols = ['#332288','#44AA99','#882255','#DDCC77', '#117733', '#88CCEE','#999933','#CC6677','#AA4499']
import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys
import matplotlib.pyplot as plt

def load_ensemble(folders,filename,years,riverine=0.65):
    out = np.zeros((len(years),len(folders))); out[:] = np.nan
    t= 0;
    for folder in folders:
        file = os.path.join(folder,filename)
        data = np.loadtxt(file,delimiter=',',skiprows=1)
        # print(data)

        s = data[0,0]
        e = data[-1,0]
        print(s)
        print(e)
        f = np.where(years == s)[0][0]
        print(f)
        g = np.where(years == e)[0][0]
        out[f:g+1,t] = -data[:,1] + riverine
        t = t+1
    return out

flux_loc = 'E:/SOCOMV2/EX5/Output/fluxes'
gcb_file = 'GCB2024_meanoceansink.csv'
years = np.array(range(1980,2024,1))


EXP0 = glob.glob(flux_loc+'/EXP0*')
EXP0_out = load_ensemble(EXP0,'annual_flux.csv',years)

EXP1 = glob.glob(flux_loc+'/EXP1*')
EXP1_out = load_ensemble(EXP1,'annual_flux.csv',years)
EXP1_cool_out = load_ensemble(EXP1,'annual_flux_salty_cool_skin.csv',years)

GCB = np.loadtxt(gcb_file,delimiter=',',skiprows=1)

fig = plt.figure(figsize = (7,7))
for i in range(EXP0_out.shape[1]):
    plt.plot(years,EXP0_out[:,i],color=cols[1],linewidth=0.5)
plt.plot(years,np.nanmean(EXP0_out,axis=1),color=cols[1],linewidth=3,label='No Correction')

for i in range(EXP1_out.shape[1]):
    plt.plot(years,EXP1_out[:,i],color=cols[2],linewidth=0.5)
plt.plot(years,np.nanmean(EXP1_out,axis=1),color=cols[2],linewidth=3,label='Arificial bias corrected')

for i in range(EXP1_cool_out.shape[1]):
    plt.plot(years,EXP1_cool_out[:,i],color=cols[4],linewidth=0.5)
plt.plot(years,np.nanmean(EXP1_cool_out,axis=1),color=cols[4],linewidth=3,label = 'Artificial bias + cool salty skin correction')

plt.plot(GCB[:,0],GCB[:,1],'k-',label='GCB2024 models',linewidth=3)
plt.plot(GCB[:,0],GCB[:,2],'b-',label='GCB2024 fCO2 product',linewidth=3)
plt.grid()

plt.ylim([1,4.5])
plt.xlabel('Years')
plt.ylabel('Net air-sea CO$_2$ flux including riverine flux\n(Pg C yr$^{-1}$; +ve into ocean)')
plt.legend()
plt.title('SOCOMv2 Ex5 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
fig.savefig('SOCOMv2_Ex5_output.png',dpi=300)
