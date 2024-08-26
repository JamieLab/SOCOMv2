#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 06/2024

"""
import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys

#Location of OceanICU neural network framework
oceanicu = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(os.path.join(oceanicu,'Data_Loading'))
sys.path.append(oceanicu)

import data_utils as du

output_loc = 'D:/SOCOMV2/EX2/UEPFNNU/final_output'
locations = ['D:/SOCOMV2/EX2/UEPFNNU/CESM_ETHZ_r1','D:/SOCOMV2/EX2/UEPFNNU/FESOM2_REcoM','D:/SOCOMV2/EX2/UEPFNNU/IPSL_r1','D:/SOCOMV2/EX2/UEPFNNU/MRI_ESM2_2','D:/SOCOMV2/EX2/UEPFNNU/NorESM_OC1_2']

for locat in locations:
    fil = locat.split('/')
    c = Dataset(os.path.join(locat,'output.nc'))
    lon = np.array(c['longitude'])
    lat = np.array(c['latitude'])
    fco2 = np.array(c['fco2'])
    time = np.array(c['time'])
    c.close()

    fco2 = du.lon_switch(np.transpose(fco2,[2,1,0]))
    lon = lon+180

    file = os.path.join(output_loc,'Ex2-2024_'+fil[-1]+'_dataprod_UEPFNNU_1985_2022.nc')
    outp = Dataset(file,'w',format='NETCDF4_CLASSIC')
    outp.date_created = datetime.datetime.now().strftime(('%d/%m/%Y'))
    outp.created_by = 'Daniel J. Ford (d.ford@exeter.ac.uk), Jamie D. Shutler (j.d.shutler@exeter.ac.uk) and Andrew Watson (Andrew.Watson@exeter.ac.uk)'
    outp.created_from = 'Data created from ' + locat
    outp.method_citation = 'Watson, A.J., Schuster, U., Shutler, J.D. et al. Revised estimates of ocean-atmosphere CO2 flux are consistent with ocean carbon inventory. Nat Commun 11, 4422 (2020). https://doi.org/10.1038/s41467-020-18203-3'
    outp.method_citation_updates = 'Preprint: Daniel J Ford, Josh Blannin, Jennifer Watts, et al. A comprehensive analysis of air-sea CO2 flux uncertainties constructed from surface ocean data products. ESS Open Archive . April 01, 2024. https://doi.org/10.22541/essoar.171199280.05732707/v1'

    outp.createDimension('lon',lon.shape[0])
    outp.createDimension('lat',lat.shape[0])
    outp.createDimension('time',time.shape[0])

    sst_o = outp.createVariable('spco2','f4',('time','lat','lon'),zlib=True)
    sst_o[:] = fco2
    sst_o.units = 'uatm'
    sst_o.standard_name = 'Surface ocean pCO2'

    sst_o = outp.createVariable('lat','f4',('lat'))
    sst_o[:] = lat
    sst_o.units = 'Degrees'
    sst_o.standard_name = 'Latitude'

    sst_o = outp.createVariable('lon','f4',('lon'))
    sst_o[:] = lon
    sst_o.units = 'Degrees'
    sst_o.standard_name = 'Longitude'

    sst_o = outp.createVariable('time','f4',('time'))
    sst_o[:] = time
    sst_o.units = 'Days since 1970-01-15'
    sst_o.standard_name = 'Time'

    outp.close()
