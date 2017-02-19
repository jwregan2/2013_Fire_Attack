import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
from dateutil.relativedelta import relativedelta
from itertools import cycle

# Set file locations

data_location = '../Data/Calibration_Tests/'

chart_location = '../../Report/Script_Figures/Entrainment/'

info_file = '../Data/Calibration_Tests/Description_of_calibration.csv'
plot_file = '../Info/description_of_charts.csv'

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Test_Name')
# Set files to skip in experimental directory
skip_files = ['kestrel','description_of_calibration']

channels = ['BDP1DoorV','BDP2DoorV','BDP3DoorV','BDP4DoorV','BDP5DoorV']



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
		data_copy = data_copy.rolling(window=1, center=True).mean()
		data_copy.insert(0, 'Elapsed Time', Exp_Data['Elapsed Time'])
		data_copy = data_copy.dropna()
		Exp_Data = data_copy

		# temp = Exp_Des['Fan_Speed'][k].split('|')
		# fan_speed = np.asarray(temp)
		# temp2 = Exp_Des['Fan_Speed_CFM'][k].split('|')
		# fan_speed_cfm = np.asarray(temp2)

		# Get experiment name from file
		Test_Name = experiment[:-4]

		# temp_time = []
		# for i in range(len(Event_Time)):
		# 	temp_time.append(Event_Time[i].timestamp() - Event_Time[0].timestamp())
		# Exp_Events['Elapsed_Time'] = temp_time
		# Start_Time = Exp_Events['Elapsed_Time'][0]
		# End_Time = temp_time[-1]

		conv_inch_h2o = 0.04

		print (Test_Name)

		area = 17.778
		for channel in channels:
			#Calculate velocity
			conv_pascal = 248.84
			convert_ftpm = 196.85
			end_zero_time = int(120)
			zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
			pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel]-zero_voltage)  # Convert voltage to pascals
			# Calculate flowrate
			Exp_Data[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * ((Exp_Des['Temp_C'][Test_Name])+273.13)) * np.sign(pressure)

		#Calculate cfm
		CFM = area*np.mean(Exp_Data[channels],axis=1)
		CFM_1 = area*(Exp_Data[channels[2]])
		CFM_3 = area*np.mean(Exp_Data[channels[1:3]],axis=1)
		zero_CFM = np.mean(CFM[0:end_zero_time])
		zero_CFM_1 = np.mean(CFM_1[0:end_zero_time])
		zero_CFM_3 = np.mean(CFM_3[0:end_zero_time])
		CFM = CFM - zero_CFM
		CFM_1 = CFM_1 - zero_CFM_1
		CFM_3 = CFM_3 - zero_CFM_3
		# cfm_avgs = []
		# for i in range(1,len(Exp_Events)):
		# 	pos2 = int(Exp_Events['Elapsed_Time'][i])
		# 	pos1 = int(Exp_Events['Elapsed_Time'][i-1])
		# 	cfm_avgs.append(np.mean(CFM[pos1:pos2]))
		# cfm_avgs = np.append(cfm_avgs,0)
		# Exp_Events['CFM_Avg'] = cfm_avgs
		# Exp_Events.to_csv('../Experimental_Data/'+ Test_Name + '_Events_CFM.csv')
		time = list(range(len(Exp_Data)))

		fig = figure()
		plt.plot(time,CFM,'r--',linewidth=1.5)
		plt.plot(time,CFM_3,'b--',label='CFM Middle 3')
		plt.plot(time,CFM_1,'r-.',label='CFM Middle')
		# for i in range(1,len(Exp_Events)):
		# 	plt.plot([Exp_Events['Elapsed_Time'][i-1],Exp_Events['Elapsed_Time'][i]],[cfm_avgs[i-1],cfm_avgs[i-1]],color='black',linewidth=2)
		ax1 = plt.gca()
		handles1, labels1 = ax1.get_legend_handles_labels()
		ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
		ax1_xlims = ax1.axis()[0:2]
		# plt.xlim([0, End_Time-Start_Time])
		plt.xlabel('Time (s)')
		plt.ylabel('CFM (ft$^3$/min)')
		try:
			# Add vertical lines and labels for timing information (if available)
			ax3 = ax1.twiny()
			ax3.set_xlim(ax1_xlims)
			# Remove NaN items from event timeline
			events = Exp_Events['Event']
			[plt.axvline(_x, color='0.50', lw=1) for _x in Exp_Events['Elapsed_Time']]
			ax3.set_xticks(Exp_Events['Elapsed_Time'])
			plt.setp(plt.xticks()[1], rotation=40)
			ax3.set_xticklabels(events.values, fontsize=8, ha='left')
			plt.xlim([0, End_Time])
			# Increase figure size for plot labels at top
			fig.set_size_inches(10, 9)
		except:
			pass
		# plt.legend(handles1, labels1, loc='upper left', fontsize=12, handlelength=3)
		savefig(chart_location+Test_Name+'_CFM.pdf')
		close()
