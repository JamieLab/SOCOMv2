#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 05/2025

"""
cols = ['#332288','#44AA99','#882255','#DDCC77', '#117733', '#88CCEE','#999933','#CC6677','#AA4499']
let = ['a','b','c','d','e','f','g','h','i','j']
import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.transforms

def load_ensemble(folders,filename,years,riverine=0.65):
    out = np.zeros((len(years),len(folders))); out[:] = np.nan
    out_unc = np.zeros((len(years),len(folders))); out_unc[:] = np.nan
    area =np.zeros((len(years),len(folders))); area[:] = np.nan
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
        out_unc[f:g+1,t] = np.sqrt(np.sum(data[:,6:]**2,axis=1))
        area[f:g+1,t] = data[:,5]
        t = t+1
    return out,out_unc,area

def correct_icefree_area(flux,unc,area):
    for i in range(area.shape[0]):
        max = np.amax(area[i,:])
        print(max)
        for j in range(area.shape[1]):
            if area[i,j]/max <0.99:
                flux[i,j] = flux[i,j] * (1/(area[i,j]/max))
                unc[i,j] = unc[i,j] * (1/(area[i,j]/max))
    return flux,unc

plot_OC4C = False
flux_loc = 'E:/SOCOMV2/EX5/Output/fluxes'
gcb_file = 'GCB2024_meanoceansink.csv'
years = np.array(range(1980,2024,1))


EXP0 = glob.glob(flux_loc+'/EXP0*')
EXP0_out,EXP0_unc,EXP0_area = load_ensemble(EXP0,'annual_flux.csv',years)

EXP0_out,EXP0_unc = correct_icefree_area(EXP0_out,EXP0_unc,EXP0_area)


EXP1 = glob.glob(flux_loc+'/EXP1*')
EXP1_out,EXP1_unc,EXP1_area = load_ensemble(EXP1,'annual_flux.csv',years)

EXP1_out,EXP1_unc = correct_icefree_area(EXP1_out,EXP1_unc,EXP1_area)

EXP1_cool_out,EXP1_cool_unc,EXP1_cool_area = load_ensemble(EXP1,'annual_flux_salty_cool_skin.csv',years)
EXP1_cool_out,EXP1_cool_unc = correct_icefree_area(EXP1_cool_out,EXP1_cool_unc,EXP1_cool_area)

GCB = np.loadtxt(gcb_file,delimiter=',',skiprows=1)

fig = plt.figure(figsize = (7,7))
for i in range(EXP0_out.shape[1]):
    plt.plot(years,EXP0_out[:,i],color=cols[1],linewidth=0.5)
    # plt.fill_between(years,EXP0_out[:,i]-EXP0_unc[:,i],EXP0_out[:,i]+EXP0_unc[:,i],color=cols[1],alpha=0.2,zorder=-1)
uncorr_mean = np.nanmean(EXP0_out,axis=1)
uncorr_unc = np.nanmean(EXP0_unc,axis=1)
plt.plot(years,uncorr_mean,color=cols[1],linewidth=3,label='No Correction')
plt.fill_between(years,uncorr_mean-uncorr_unc,uncorr_mean+uncorr_unc,color=cols[1],alpha=0.2,zorder=-1)


for i in range(EXP1_out.shape[1]):
    plt.plot(years,EXP1_out[:,i],color=cols[2],linewidth=0.5)

corr_mean = np.nanmean(EXP1_out,axis=1)
corr_unc = np.nanmean(EXP1_unc,axis=1)
plt.plot(years,corr_mean,color=cols[2],linewidth=3,label='Arificial bias corrected')
plt.fill_between(years,corr_mean-corr_unc,corr_mean+corr_unc,color=cols[2],alpha=0.2,zorder=-1)

for i in range(EXP1_cool_out.shape[1]):
    plt.plot(years,EXP1_cool_out[:,i],color=cols[4],linewidth=0.5)
# plt.plot(years,np.nanmean(EXP1_cool_out,axis=1),color=cols[4],linewidth=3,label = 'Artificial bias + cool salty skin correction')
corr_cool_mean = np.nanmean(EXP1_cool_out,axis=1)
corr_cool_unc = np.nanmean(EXP1_cool_unc,axis=1)
plt.plot(years,corr_cool_mean,color=cols[4],linewidth=3,label = 'Artificial bias + cool salty skin correction')
plt.fill_between(years,corr_cool_mean-corr_cool_unc,corr_cool_mean+corr_cool_unc,color=cols[4],alpha=0.2,zorder=-1)

plt.plot(GCB[:,0],GCB[:,1],'k--',label='GCB2024 models',linewidth=2)
plt.plot(GCB[:,0],GCB[:,2],'b--',label='GCB2024 fCO2 product',linewidth=2)
plt.grid()

plt.ylim([1,4.5])
plt.xlabel('Years')
plt.ylabel('Net air-sea CO$_2$ flux including riverine flux\n(Pg C yr$^{-1}$; +ve into ocean)')
plt.legend()
plt.title('SOCOMv2 Ex5 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
fig.savefig('SOCOMv2_Ex5_output.png',dpi=300)
plt.title('')
fig.savefig('SOCOMv2_Ex5_output_notitle.png',dpi=300)

print(years.shape)
print(uncorr_mean.shape)
output = np.transpose(np.vstack((years,uncorr_mean,uncorr_unc,corr_mean,corr_unc,corr_cool_mean,corr_cool_unc)))
np.savetxt('EX5_output.csv',output,delimiter=',',header='Years,uncorrected_mean,uncorrected_uncertainty,corrected_mean,corrected_uncertainty,corrected+cool_mean,corrected+cool_uncertainty')

print(EXP0_out.shape)
output = np.c_[ years, EXP0_out ]
np.savetxt('EX5_output_EXP0.csv',output,delimiter=',')

output = np.c_[ years, EXP1_out ]
np.savetxt('EX5_output_EXP1.csv',output,delimiter=',')

output = np.c_[ years, EXP1_cool_out ]
np.savetxt('EX5_output_EXP1_cool.csv',output,delimiter=',')



for i in range(len(EXP0)):
    print(EXP0[i])
    meth= EXP0[i].split('_')[1]

    uncorr,uncorr_unc,uncorr_area = load_ensemble([os.path.join(flux_loc,'EXP0_'+meth)],'annual_flux.csv',years)

    corr,corr_unc,corr_area = load_ensemble([os.path.join(flux_loc,'EXP1_'+meth)],'annual_flux.csv',years)
    corr_cool,corr_cool_unc,corr_cool_area = load_ensemble([os.path.join(flux_loc,'EXP1_'+meth)],'annual_flux_salty_cool_skin.csv',years)
    fig = plt.figure(figsize = (7,7))
    plt.plot(years,uncorr,color=cols[1],linewidth=3,label='No Correction')
    plt.fill_between(years,np.squeeze(uncorr-uncorr_unc),np.squeeze(uncorr+uncorr_unc),color=cols[1],alpha=0.2,zorder=-1)
    plt.plot(years,corr,color=cols[2],linewidth=3,label='Arificial bias corrected')
    plt.fill_between(years,np.squeeze(corr-corr_unc),np.squeeze(corr+corr_unc),color=cols[2],alpha=0.2,zorder=-1)
    plt.plot(years,corr_cool,color=cols[4],linewidth=3,label = 'Artificial bias + cool salty skin correction')
    plt.fill_between(years,np.squeeze(corr_cool-corr_cool_unc),np.squeeze(corr_cool+corr_cool_unc),color=cols[4],alpha=0.2,zorder=-1)
    plt.xlabel('Years')
    plt.ylabel('Net air-sea CO$_2$ flux including riverine flux\n(Pg C yr$^{-1}$; +ve into ocean)')
    plt.legend(loc = 8)
    plt.grid()
    plt.ylim([0.5,4.5])
    plt.xlim([1980,2023])
    #plt.title('SOCOMv2 Ex5 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
    fig.savefig('plots/SOCOMv2_Ex5_output_'+meth+'.png',dpi=300)

if plot_OC4C:
    meth_li = ['UExP-FNN-U','sfCO2-Residual','LDEO','CMEMS-LSCE-FFNNv3']
    font = {'weight' : 'normal',
            'size'   : 16}
    matplotlib.rc('font', **font)
    fig = plt.figure(figsize=(14,14))
    gs = GridSpec(2,2, figure=fig, wspace=0.25,hspace=0.17,bottom=0.05,top=0.97,left=0.1,right=0.95)
    ax = [fig.add_subplot(gs[0, 0]),fig.add_subplot(gs[0,1]),fig.add_subplot(gs[1, 0]),fig.add_subplot(gs[1, 1])]
    for i in range(len(meth_li)):
        # print(EXP0[i])
        # meth= EXP0[i].split('_')[1]
        meth = meth_li[i]

        uncorr,uncorr_unc,uncorr_area = load_ensemble([os.path.join(flux_loc,'EXP0_'+meth)],'annual_flux.csv',years)
        corr,corr_unc,corr_area = load_ensemble([os.path.join(flux_loc,'EXP1_'+meth)],'annual_flux.csv',years)
        corr_cool,corr_cool_unc,corr_cool_area = load_ensemble([os.path.join(flux_loc,'EXP1_'+meth)],'annual_flux_salty_cool_skin.csv',years)

        ax[i].plot(years,uncorr,color=cols[1],linewidth=3,label='No Correction')
        ax[i].plot(years,corr,color=cols[2],linewidth=3,label='Arificial bias corrected')
        ax[i].plot(years,corr_cool,color=cols[4],linewidth=3,label = 'Artificial bias + cool salty skin correction')
        ax[i].fill_between(years,np.squeeze(uncorr-uncorr_unc),np.squeeze(uncorr+uncorr_unc),color=cols[1],alpha=0.2,zorder=-1)
        ax[i].fill_between(years,np.squeeze(corr-corr_unc),np.squeeze(corr+corr_unc),color=cols[2],alpha=0.2,zorder=-1)
        ax[i].fill_between(years,np.squeeze(corr_cool-corr_cool_unc),np.squeeze(corr_cool+corr_cool_unc),color=cols[4],alpha=0.2,zorder=-1)
        ax[i].set_xlabel('Years')
        ax[i].set_ylabel('Net air-sea CO$_2$ flux including riverine flux\n(Pg C yr$^{-1}$; +ve into ocean)')
        ax[i].legend(fontsize=14,loc=8)
        ax[i].grid()
        ax[i].set_ylim([0.5,4.5])
        ax[i].set_xlim([1980,2023])
        ax[i].text(0.92,0.97,f'('+let[i]+')',transform=ax[i].transAxes,va='top',fontweight='bold',fontsize = 20)
        if meth == 'LDEO':
            meth = 'LDEO-HPD'
        if meth == 'CMEMS-LSCE-FFNNv3':
            meth = 'CMEMS-LSCE-FFNN'
        ax[i].text(0.04,0.97,meth,transform=ax[i].transAxes,va='top',fontweight='bold',fontsize = 20)
        #plt.title('SOCOMv2 Ex5 - '+datetime.datetime.now().strftime(('%d/%m/%Y %H:%M')))
    fig.savefig('plots/SOCOMv2_Ex5_output_OC4C_deliverable.png',dpi=300)


EXP0 = glob.glob(flux_loc+'/EXP0*')
EXP0_out,EXP0_unc,EXP0_area = load_ensemble(EXP0,'annual_flux_night_nocoolskin.csv',years)

EXP0_out,EXP0_unc = correct_icefree_area(EXP0_out,EXP0_unc,EXP0_area)


EXP1 = glob.glob(flux_loc+'/EXP1*')
EXP1_out,EXP1_unc,EXP1_area = load_ensemble(EXP1,'annual_flux_night_nocoolskin.csv',years)

EXP1_out,EXP1_unc = correct_icefree_area(EXP1_out,EXP1_unc,EXP1_area)

EXP1_cool_out,EXP1_cool_unc,EXP1_cool_area = load_ensemble(EXP1,'annual_flux_night_salty_cool_skin.csv',years)
EXP1_cool_out,EXP1_cool_unc = correct_icefree_area(EXP1_cool_out,EXP1_cool_unc,EXP1_cool_area)

uncorr_mean = np.nanmean(EXP0_out,axis=1)
uncorr_unc = np.nanmean(EXP0_unc,axis=1)
corr_mean = np.nanmean(EXP1_out,axis=1)
corr_unc = np.nanmean(EXP1_unc,axis=1)
corr_cool_mean = np.nanmean(EXP1_cool_out,axis=1)
corr_cool_unc = np.nanmean(EXP1_cool_unc,axis=1)
output = np.transpose(np.vstack((years,uncorr_mean,uncorr_unc,corr_mean,corr_unc,corr_cool_mean,corr_cool_unc)))
np.savetxt('EX5_output_nightingale.csv',output,delimiter=',',header='Years,uncorrected_mean,uncorrected_uncertainty,corrected_mean,corrected_uncertainty,corrected+cool_mean,corrected+cool_uncertainty')

EXP0 = glob.glob(flux_loc+'/EXP0*')
EXP0_out,EXP0_unc,EXP0_area = load_ensemble(EXP0,'annual_flux_night_nocoolskin_ccmp.csv',years)

EXP0_out,EXP0_unc = correct_icefree_area(EXP0_out,EXP0_unc,EXP0_area)


EXP1 = glob.glob(flux_loc+'/EXP1*')
EXP1_out,EXP1_unc,EXP1_area = load_ensemble(EXP1,'annual_flux_night_nocoolskin_ccmp.csv',years)

EXP1_out,EXP1_unc = correct_icefree_area(EXP1_out,EXP1_unc,EXP1_area)

EXP1_cool_out,EXP1_cool_unc,EXP1_cool_area = load_ensemble(EXP1,'annual_flux_night_salty_cool_skin_ccmp.csv',years)
EXP1_cool_out,EXP1_cool_unc = correct_icefree_area(EXP1_cool_out,EXP1_cool_unc,EXP1_cool_area)

uncorr_mean = np.nanmean(EXP0_out,axis=1)
uncorr_unc = np.nanmean(EXP0_unc,axis=1)
corr_mean = np.nanmean(EXP1_out,axis=1)
corr_unc = np.nanmean(EXP1_unc,axis=1)
corr_cool_mean = np.nanmean(EXP1_cool_out,axis=1)
corr_cool_unc = np.nanmean(EXP1_cool_unc,axis=1)
output = np.transpose(np.vstack((years,uncorr_mean,uncorr_unc,corr_mean,corr_unc,corr_cool_mean,corr_cool_unc)))
np.savetxt('EX5_output_nightingale_ccmp.csv',output,delimiter=',',header='Years,uncorrected_mean,uncorrected_uncertainty,corrected_mean,corrected_uncertainty,corrected+cool_mean,corrected+cool_uncertainty')
