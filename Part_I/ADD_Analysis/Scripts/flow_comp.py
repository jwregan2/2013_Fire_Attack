import pandas as pd 
from scipy import stats 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
from dateutil.relativedelta import relativedelta
from itertools import cycle


data_dir = '../CSV_Data/'
info_file = '../Info/Description_of_Experiments.csv'
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Original_Test_Name')
comp_file = '../Info/test_differences.csv'
comp_des = pd.read_csv(comp_file)

p_val = []
f_val = []

for ii in range(len(comp_des)):
	print(comp_des['Name'][ii])
	num_tests = comp_des['Number_of_Tests'][ii]
	data = []
	names = []
	names = comp_des['Experiments_To_Compare'][ii].split('|')
	for nn in range(num_tests):
		globals() ["data"+str(nn+1)] = pd.read_csv(data_dir+names[nn-1]+'_Datafile.csv')
		globals() ["total_water_buckets_"+str(nn+1)] = []
		for jj in range(1,49):
			globals() ["total_water_buckets_"+str(nn+1)].append(globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[-1] - globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[0])		
		globals() ["total_water_buckets_"+str(nn+1)] = globals() ["total_water_buckets_"+str(nn+1)] / (max(globals() ["total_water_buckets_"+str(nn+1)]))
	
	data_dict ={}
	for kk in range(num_tests):
		data_dict["total_water_buckets_"+str(kk+1)] = globals() ["total_water_buckets_"+str(kk+1)]

	f_val_temp, p_val_temp = stats.f_oneway(*data_dict.values())
	f_val.append(f_val_temp)
	p_val.append(p_val_temp)

comp_des['P_Test'] = p_val
comp_des['F_Test'] = f_val
comp_des.to_csv('../Info/test_differences_output.csv')

