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
		# print (Exp_Data['Time'][1])
		# Exp_Time = [datetime.datetime.strptime(t, '%d/%m/%Y %H:%M:%S') for t in Exp_Data['Time']]
		# print(Exp_Time)
		Exp_Events = pd.read_csv(data_location + experiment[:-4]+'_Events.csv')
		Event_Time = [datetime.datetime.strptime(t, '%Y-%m-%d-%H:%M:%S') for t in Exp_Events['Time']]
		print(Event_Time)
		print(fds)

		# Get experiment name from file
		Test_Name = experiment[:-4]
		Exp_Num = Test_Name[4:-7]

		BDP_Resolution = Exp_Des['BDP_Res'][Test_Name]

		if BDP_Resolution == 'N':
			channels = channels_nr
		else:
			channels = channels_hr

		print ()
		print (Test_Name)

		for channel in channels:
			#Calculate velocity in ft/min
			zero_voltage = np.mean(Exp_Data[channel][0:60])
			Exp_Data[channel] = (np.sign(Exp_Data[channel]-zero_voltage)*0.070*(288.7*(4.98*abs(Exp_Data[channel]-zero_voltage)))**0.5) * 196.85

		#Calculate cfm
		area = 18.56
		CFM = np.mean(Exp_Data[channels],axis=1)*area


