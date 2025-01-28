#!/usr/bin/env python3
import numpy as np
import datetime
from netCDF4 import Dataset
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

output_file = 'output.nc'

c = Dataset(output_file,'r')
flux = np.array(c['JMA-MLR_fgco2'])
unc = np.array(c['JMA-MLR_unc'])
lon = np.array(c['longitude'])
lat = np.array(c['latitude'])
c.close()

data = np.abs(flux) * unc
fig = plt.figure(figsize=(14,7))
gs = GridSpec(1,1, figure=fig, wspace=0.3,hspace=0.3,bottom=0.1,top=0.95,left=0.10,right=0.98)

ax = fig.add_subplot(gs[0,0])
a = ax.pcolor(lon,lat,np.transpose(data[:,:,0]),vmin=0,vmax=0.1,cmap='Blues')
ax.set_facecolor('gray')
cbar = plt.colorbar(a)
cbar.set_label('Air-sea CO$_{2}$ flux uncertainty (g C m$^{-2}$ d$^{-1}$)')
fig.savefig(os.path.join('plots','example_flux_unc.png'),format='png',dpi=300)
