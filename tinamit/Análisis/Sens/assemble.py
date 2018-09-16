from __future__ import print_function
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.graphics.api import qqplot


#ARIMA(p,d,q)
# step 1, confirm d
# dt = [3.93,	4.31,	3.99,	4.56,	4.70,	4.43,	3.66,	3.78,	4.57,	4.06,	5.21,	4.35,	4.38,	4.30,	3.93,	4.35,	4.32,	3.55,	4.07,	4.16,	3.99,	4.26,	2.80,	3.55,	3.68,	3.35,	3.37,	3.42,	3.33,	3.44,	3.48,	3.69,	4.54,	4.88,	5.07,	5.10,	4.84,	5.71,	5.26, 5.79,	6.17,	6.70,	7.04,	6.87,	6.84,	6.79,	6.79,	7.23]
# dta = pd.Series(dt)
# dta.index = pd.Index(sm.tsa.datetools.dates_from_range('2000','2047'))
# dta.plot(figsize=(12,8)) # original observed dt

# fig = plt.figure(figsize=(12,8))
# ax1= fig.add_subplot(111)
# diff1 = dta.diff(1)
# diff1.plot(ax=ax1)

# fig = plt.figure(figsize=(12,8))
# ax2= fig.add_subplot(111)
# diff2 = dta.diff(2)
# diff2.plot(ax=ax2)
#
# fig = plt.figure(figsize=(12,8))
# ax3= fig.add_subplot(111)
# diff3 = dta.diff(3)
# diff3.plot(ax=ax3)

# STEP 2 confirm p,d, 检查平稳时间序列的自相关图和偏自相关图
# dta= dta.diff(1)# obs the diff1, 2,3 --> use diff 1
# fig = plt.figure(figsize=(12,8))
# ax1=fig.add_subplot(211)
# # lags = 滞后的阶数
# fig = sm.graphics.tsa.plot_acf(dta,lags=40,ax=ax1)
# ax2 = fig.add_subplot(212)
# fig = sm.graphics.tsa.plot_pacf(dta,lags=40,ax=ax2)

dta=[10930,10318,10595,10972,7706,6756,9092,10551,9722,10913,11151,8186,6422,
6337,11649,11652,10310,12043,7937,6476,9662,9570,9981,9331,9449,6773,6304,9355,
10477,10148,10395,11261,8713,7299,10424,10795,11069,11602,11427,9095,7707,10767,
12136,12812,12006,12528,10329,7818,11719,11683,12603,11495,13670,11337,10232,
13261,13230,15535,16837,19598,14823,11622,19391,18177,19994,14723,15694,13248,
9543,12872,13101,15053,12619,13749,10228,9725,14729,12518,14564,15085,14722,
11999,9390,13481,14795,15845,15271,14686,11054,10395]

dta=pd.Series(dta)
dta.index = pd.Index(sm.tsa.datetools.dates_from_range('2001','2090'))
dta.plot(figsize=(12,8))
