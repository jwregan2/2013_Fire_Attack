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
bin_file = '../Info/bin_map.csv'
bin_data = pd.read_csv(bin_file)


p_val_rate = []
p_val_total = []
stat_diff = []
stat_diff2 = []

for ii in range(len(comp_des)):
	print(comp_des['Name'][ii])
	num_tests = comp_des['Number_of_Tests'][ii]
	data = []
	names = []
	names = comp_des['Experiments_To_Compare'][ii].split('|')
	for nn in range(num_tests):
		globals() ["data"+str(nn+1)] = pd.read_csv(data_dir+names[nn-1]+'_Datafile.csv')
		globals() ["rate_water_buckets_"+str(nn+1)] = []
		globals() ["total_water_buckets_"+str(nn+1)] = []
		init_water = 0
		final_water = 0
		for jj in range(1,49):
			init_water = globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[0]+init_water
			final_water = globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[-1]+final_water
		for k in range(len(globals() ["data"+str(nn+1)])):
			water_flow = 0
			for jj in range(1,49):
				water_flow = globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[k]+water_flow		
			if (water_flow - init_water) > 5:
				break
		for kk in range(len(globals() ["data"+str(nn+1)])):
			water_flow = 0
			for jj in range(1,49):
				water_flow = globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[kk]+water_flow		
			if (final_water-water_flow) < 5:
				break
		for jj in range(1,49):	
			globals() ["total_water_buckets_"+str(nn+1)].append(globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[-1] - globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Scaled'].iloc[0])		
			globals() ["rate_water_buckets_"+str(nn+1)].append(globals() ["data"+str(nn+1)]['Pressure_'+str(jj)+'- Rate'].iloc[k:kk].mean())
	
	data_dict_rate = {}
	data_dict_total = {}
	for kk in range(num_tests):
		data_dict_rate["rate_water_buckets_"+str(kk+1)] = globals() ["rate_water_buckets_"+str(kk+1)]/bin_data['area']
		data_dict_total["total_water_buckets_"+str(kk+1)] = globals() ["total_water_buckets_"+str(kk+1)]
	
	f_val_temp,p_val_temp1 = stats.kruskal(*data_dict_rate.values())
	p_val_rate.append(p_val_temp1)
	f_val_temp,p_val_temp2 = stats.kruskal(*data_dict_total.values())
	p_val_total.append(p_val_temp2)

	if p_val_temp1 < 0.05:
		stat_diff.append('yes')
	else:
		stat_diff.append('no')

	if p_val_temp2 < 0.05:
		stat_diff2.append('yes')
	else:
		stat_diff2.append('no')


comp_des['P_Test_Rate'] = p_val_rate
comp_des['Are Rates Different'] = stat_diff
comp_des['P_Test_Total'] = p_val_total
comp_des['Are Totals Different'] = stat_diff2

comp_des.to_csv('../Info/test_differences_output.csv')




