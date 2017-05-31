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
import scipy.optimize as sop
#%%
def quad(x, a, b, c):
    return (a * (x**2)) + b * x + c
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
ir_mat = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2]

ir = np.zeros(7)
ir[0] = 4 * np.log(1 + (libor['PX_MID'] / 100) * 0.25)

dct = np.zeros(7)
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
irterm = pd.DataFrame(ir, index = ir_mat, columns = ['IR'])
irterm['DF'] = np.exp(-irterm['IR'] * irterm.index)
#%%
swap_mat = [0.5 * i for i in range(1, 81)]
swap_term = pd.DataFrame(index = swap_mat, columns = [['SR', 'DF']])

for i in [0.5, 1, 1.5, 2]:
    swap_term['SR'][i] = irterm['IR'][i]
    swap_term['DF'][i] = irterm['DF'][i]

for i in range(3, 13):
    c = swap['PMT'][i-1]
    a = 100 + c
    y = np.sqrt(swap_term['DF'][i-1])
    c_sum = (c * swap_term['DF'][:(i-1)]).sum()
    
    sol = sop.root(quad, 100, args = (a, c * y, c_sum - 100))
    d = float(sol.x ** 2)
    r = -np.log(d) / i
    d1 = np.sqrt(d * swap_term['DF'][i-1])
    r1 = -np.log(d1) / (i - 0.5)
    
    swap_term['SR'][i] = r
    swap_term['DF'][i] = d
    swap_term['SR'][i - 0.5] = r1
    swap_term['DF'][i - 0.5] = d1
#%%
def findP(x, start, end):
    freq = (end - start) * 2
    c = swap['PMT']['USSWAP%d Curncy' %end]
    c_sum = (c * swap_term['DF'][:(start)]).sum()
    
    temp = 0
    for i in range(start, end + 1):
        temp += swap_term['DF'][start] ** ((i - start + 1) / freq) +\
                x ** ((freq - (i - start + 1)) / freq) 
    result = temp * c + 100 * x
    
    return result + c_sum - 100

matlist = [12, 15, 20, 25, 30, 40]
for i in range(len(matlist) - 1):
    d = float(sop.root(findP, 0, args = (matlist[i], matlist[i+1])).x)
    r = -np.log(d) / matlist[i+1]
    swap_term['SR'][matlist[i+1]] = r
    swap_term['DF'][matlist[i+1]] = d
