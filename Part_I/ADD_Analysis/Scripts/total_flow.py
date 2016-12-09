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

for f in os.listdir(data_dir):
	if f.endswith('.csv'):

		# Read in experiment file
		experiment = f

		data = pd.read_csv(data_dir + experiment)
		Test_Name = experiment[:-4]

		print(Test_Name)

		total_water_exp = 0
		for i in range(1,49):
			total_water_exp = (data['Pressure_'+str(i)+'- Scaled'].iloc[-1] - data['Pressure_'+str(i)+'- Scaled'].iloc[0]) + total_water_exp

		total_water_theo = Exp_Des['Flow_Rate_(gpm)'][Test_Name]*1
		print('Total Experiment Water Measured: ',total_water_exp)
		print('Total Theoretical Water Flowed: ',total_water_theo)
		print('Percent Difference: ', 100*abs(total_water_exp-total_water_theo)/total_water_theo)
		print()	
		print()
