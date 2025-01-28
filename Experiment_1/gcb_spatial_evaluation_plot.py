#!/usr/bin/env python3
import numpy as np
import datetime
from netCDF4 import Dataset
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import weight_stats as ws
import sys
import cmocean
start_yr = 1990
end_yr = 2022


output_file = 'output.nc'

c = Dataset(output_file,'r')
data = np.array(c['CMEMS-LSCE-FFNN_fgco2'])
lat = np.array(c['latitude'])
lon = np.array(c['longitude'])
c.close()

fig = plt.figure(figsize=(14,7))
gs = GridSpec(1,1, figure=fig, wspace=0.3,hspace=0.3,bottom=0.1,top=0.95,left=0.10,right=0.98)

ax = fig.add_subplot(gs[0,0])
a = ax.pcolor(lon,lat,np.transpose(np.sum(np.isnan(data[:,:,:])==0,axis=2)/data.shape[2])*100,vmin=0,vmax=100,cmap = cmocean.cm.thermal)
cbar = plt.colorbar(a)
cbar.set_label('Percentage observations in timeseries (%)')
fig.savefig(os.path.join('plots','spatial_extent.png'),format='png',dpi=300)
