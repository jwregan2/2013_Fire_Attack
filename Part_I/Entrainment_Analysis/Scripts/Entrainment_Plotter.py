import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle

# Set file locations

data_location = '../Experimental_Data/'

chart_location = '../Figures/'

info_file = '../description_of_experiments_entrainment.csv'

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Test_Name')
# Set files to skip in experimental directory
skip_files = ['_events']

channels_nr = ['BDP1V','BDP2V','BDP3V','BDP4V','BDP5V']
channels_hr = ['BDP1VHR','BDP2VHR','BDP3VHR','BDP4VHR','BDP5VHR']

# Loop through Experiment files
for f in os.listdir(data_location):
	if f.endswith('.csv'):

		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue

		# Read in experiment file
		experiment = f

		# exp = experiment[11:-9]
		Exp_Data = pd.read_csv(data_location + experiment)
		data_copy = Exp_Data.drop('Elapsed Time', axis=1)
		data_copy = data_copy.rolling(window=10, center=True).mean()
		data_copy.insert(0, 'Elapsed Time', Exp_Data['Elapsed Time'])
		data_copy = data_copy.dropna()
		Exp_Data = data_copy

		Exp_Events = pd.read_csv(data_location + experiment[:-4]+'_Events.csv')
		Event_Time = [datetime.datetime.strptime(t, '%Y-%m-%d-%H:%M:%S') for t in Exp_Events['Time']]

		# Get experiment name from file
		Test_Name = experiment[:-4]
		Exp_Num = Test_Name[4:-7]

		temp_time = []
		for i in range(len(Event_Time)):
			temp_time.append(Event_Time[i].timestamp() - Event_Time[0].timestamp() + Exp_Des['Time_Offset'][Test_Name])
		Exp_Events['Elapsed_Time'] = temp_time

		BDP_Resolution = Exp_Des['BDP_Res'][Test_Name]
		if BDP_Resolution == 'N':
			channels = channels_nr
		else:
			channels = channels_hr

		print ()
		print (Test_Name)

		for channel in channels:
			#Calculate velocity
			conv_inch_h2o = 0.4
			conv_pascal = 248.8
			convert_ftpm = 196.85
			end_zero_time = int(Exp_Events['Elapsed_Time'][1])
			zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
			pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel] - zero_voltage)  # Convert voltage to pascals
			# Calculate velocity
			Exp_Data[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (293.15)) * np.sign(pressure)

		#Calculate cfm
		area = 18.56
		CFM = np.mean(Exp_Data[channels],axis=1)*area
		cfm_avgs = []
		for i in range(1,len(Exp_Events)):
			pos2 = int(Exp_Events['Elapsed_Time'][i])
			pos1 = int(Exp_Events['Elapsed_Time'][i-1])
			cfm_avgs.append(np.mean(CFM[pos1:pos2]))
		cfm_avgs = np.append(cfm_avgs,'NaN')
		Exp_Events['CFM_Avg'] = cfm_avgs

	Exp_Events.to_csv('../Experimental_Data/'+ Test_Name + '_Events_CFM.csv')


