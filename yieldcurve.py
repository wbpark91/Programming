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

edf['Fwd'] = (edf['Fut'] / 100) - (0.5 * (edf['Vol'] ** 2) \
                                   * edf['T1'] * edf['T2'])

edffwd = edf[['Fwd', 'T1']]['EDU7 Comdty':]

swap['PMT'] = 0.5 * swap['PX_MID']
#%%
mat = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10,
       11, 12, 15, 20, 25, 30, 40]
ir = np.zeros(22)
ir[0] = 4 * np.log(1 + (libor['PX_MID'] / 100) * 0.25)

dct = np.zeros(22)
dct[0] = np.exp(-ir[0] * edffwd['T1'][0])

for i in range(len(edffwd)):
    t1 = edffwd['T1'][i]
    t2 = t1 + 0.25
    
    r = ((ir[i] * t1) + edffwd['Fwd'][i] * (t2 - t1)) / t2
    d = np.exp(-r * t2)
    ir[i+1] = r
    dct[i+1] = d

dct[6] = (100 - swap['PMT'][0] * (dct[1] + dct[3] + dct[5])) / (100 + swap['PMT'][0])
ir[6] = -np.log(dct[6]) / 2
    
#%%
term = pd.DataFrame(ir, index = mat, columns = ['IR'])
term['DF'] = np.exp(-term['IR'] * term.index)
