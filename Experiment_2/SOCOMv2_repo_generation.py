#!/usr/bin/env python3
"""
Created by Daniel J. Ford (d.ford@exeter.ac.uk)
Date: 23/04/2026

"""
import glob
import datetime
import os
from netCDF4 import Dataset
import numpy as np
import sys
import pandas as pd
import shutil
oceanicu_loc = 'C:/Users/df391/OneDrive - University of Exeter/Post_Doc_ESA_Contract/OceanICU'
sys.path.append(oceanicu_loc)
sys.path.append(os.path.join(oceanicu_loc,'Data_Loading'))
import data_utils as du

repo_version = 'v1'
repo_doi = '10.5281/zenodo.19706081'
print('Repo DOI is: '+repo_doi)
print('Check this is correct for version:' + repo_version)

base_loc = 'E:/SOCOMv2/EX2'
final_location = os.path.join(base_loc,'flux','final_output')
repo_location = os.path.join(final_location,'repo')
du.makefolder(repo_location)
g = glob.glob(os.path.join(final_location,'*.nc'))

for i in g:
    fi = i.split('\\')
    new_fi = os.path.join(repo_location,'SOCOMv2_Ex2_'+fi[-1].split('.')[0]+'_'+repo_version+'.nc')
    shutil.copy(i,new_fi)
    c = Dataset(new_fi,'a')
    c.version = repo_version
    c.contacts = 'Daniel J. Ford (d.ford@exeter.ac.uk) and Alizée Roobaert (alizee.roobaert@vliz.be)'
    c.repo_doi = repo_doi
    c.supporting_manuscript = 'Reconciling ocean carbon uptake estimates: a multi-model assessment of surface ocean CO2 reconstruction skill within the SOCOMv2 initiative. (in prep) A. Roobaert, D. J. Ford, M. G. Sreeush, G. A. McKinley, J. Hauck, A. R. Fay, T. H. Heimdal, N. Gruber, L. Bopp, F. Chevallier, L. M. Djeutchouang, M. Gehlen, L. Gregor, Y. Iida, A. Jersild, C. Rödenbeck, J. Rogerson, J. Schwinger, C. A. Shaum, H. Tsujino,  A. Watson, J. Zeng, J. D. Shutler, and P. Landschützer'
    c.code_repository = 'https://github.com/JamieLab/SOCOMv2/tree/main/Experiment_2'
    c.last_modified = datetime.datetime.now().strftime(('%d/%m/%Y %H:%M'))
    c.close()
