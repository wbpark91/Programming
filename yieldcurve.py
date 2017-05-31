#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 19:40:20 2017

@author: park-wanbae
"""
#%%
import pandas as pd
import numpy as np
import datetime as dat
from dateutil import relativedelta as reldt
#%%
libor = pd.read_excel('libor.xlsx')
edf = pd.read_excel('edf.xlsx')
swap = pd.read_excel('swap.xlsx')
vol = pd.read_excel('vol.xlsx', index_col = 0) / 10000

today = dat.datetime(2017, 5, 31)
#%%
edf['Fut'] = 100 - edf['PX_MID']
impvol = np.array(vol['1Yr'][:'2Yr'])
impvol[5] = impvol[4]
edf['Vol'] = impvol

day = np.zeros(6)
day_temp = edf['FUT_CONTRACT_DT'] - today

for i in range(len(day)):
    day[i] = (day_temp[i]).days

edf['T1'] = day / 360
edf['T2'] = (day + 90) / 360

edf['Fwd'] = (edf['Fut'] / 100) - (0.5 * (edf['Vol'] ** 2) * edf['T1'] * edf['T2'])