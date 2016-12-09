import pandas as pd 
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
skip_files = ['water']

total_water_theo =[]
total_water_exp = []
percent_diff = []
name = []
for f in os.listdir(data_dir):
	if f.endswith('.csv'):

		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue
	
		# Read in experiment file
		experiment = f

		Test_Name = experiment[:-4]
		if Exp_Des['Test_Config'][Test_Name] == 'ignore':
			continue
		name.append(Test_Name)
		print(Test_Name)
		data = pd.read_csv(data_dir + experiment)

		total_water_exp_temp = 0
		for i in range(1,49):
			total_water_exp_temp = (data['Pressure_'+str(i)+'- Scaled'].iloc[-1] - data['Pressure_'+str(i)+'- Scaled'].iloc[0]) + total_water_exp_temp
		total_water_theo_temp = Exp_Des['Flow_Rate_(gpm)'][Test_Name]*1
		percent_diff.append(round(100*abs(total_water_exp_temp-total_water_theo_temp)/total_water_theo_temp,2))

		total_water_exp.append(total_water_exp_temp)
		total_water_theo.append(total_water_theo_temp)	

output = [name,total_water_theo,total_water_exp,percent_diff]
cols = ['Test Name', 'Theoretical Water', 'Experimental Water', 'Percent Difference']
df = pd.DataFrame(np.transpose(output),columns=cols)
df.to_csv(data_dir+'Water_Output_Comparison.csv')
