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

inps = 'D:/SOCOMV2/EX2/flux'
start_yr = 1970
end_yr = 2022
log,lag = du.reg_grid(lat=1,lon=1)
from Data_Loading.ERA5_data_download import era5_average
era5_average(loc = "D:/Data/ERA5/MONTHLY/DATA", outloc=os.path.join(inps,'si10'),log=log,lag=lag,var='si10',start_yr = start_yr,end_yr =end_yr)
era5_average(loc = "D:/Data/ERA5/MONTHLY/DATA", outloc=os.path.join(inps,'msl'),log=log,lag=lag,var='msl',start_yr = start_yr,end_yr =end_yr)

from Data_Loading.interpolate_noaa_ersl import interpolate_noaa
interpolate_noaa('D:/Data/NOAA_ERSL/2024_download.txt',grid_lon = log,grid_lat = lag,out_dir = os.path.join(inps,'xco2atm'),start_yr=start_yr,end_yr = end_yr)

import Data_Loading.gebco_resample as ge
ge.gebco_resample('D:/Data/Bathymetry/GEBCO_2023.nc',log,lag,save_loc = os.path.join(inps,'bath.nc'),save_loc_fluxengine = os.path.join(inps,'fluxengine_bath.nc'))
