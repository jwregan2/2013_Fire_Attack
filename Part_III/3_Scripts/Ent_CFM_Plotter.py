##########################################################
# Script generates CFM plots from BDP1 (window) and BDP4 #
# 	(hallway door) data for entrainment experiments      #
##########################################################
import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
from dateutil.relativedelta import relativedelta
from itertools import cycle
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
from matplotlib import colors as mcolors
from scipy.signal import savgol_filter

# Set file locations
data_location = '../0_Data/Ent_Experiment_Data/CSV/'
event_location = '../1_Info/Ent/Events/'
chart_location = '../2_Plots/Ent_Experiment_Plots/'

# Read in description of experiments; set index of description of experiments
info_file = '../1_Info/Ent/Description_of_Experiments.csv'
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Experiment')

BDP1_channels = ['BDP11V','BDP12V','BDP13V','BDP14V','BDP15V']
BDP4_channels = ['BDP41V','BDP42V','BDP43V','BDP44V','BDP45V']

# Loop through Experiment files
for f in os.listdir(data_location):
	if f.endswith('.csv'):
		# Read in experiment file
		File_Name = f[:-4]

		# Get experiment name from file
		Test_Name = File_Name[:-5]
		Exp_Num = Test_Name[11:]

		print(Test_Name)
		
		skip_channels = Exp_Des['Excluded Channels'][File_Name].split('|')
		
		# Savgol filter
		# Raw_Data = pd.read_csv(data_location + f)
		# Exp_Data = pd.DataFrame(Raw_Data['Elapsed Time'].values.astype(object), columns=['Elapsed Time'])
		# data_copy = Raw_Data.drop('Elapsed Time', axis=1)
		# data_copy = data_copy.drop('Time', axis=1)
		# for column in data_copy:
		# 	filtered_data = savgol_filter(data_copy[column],11,3)
		# 	Exp_Data[column] = filtered_data

		# Moving average filter
		Exp_Data = pd.read_csv(data_location + f)
		data_copy = Exp_Data.drop('Elapsed Time', axis=1)
		data_copy = data_copy.rolling(window=5, center=True).mean()
		data_copy.insert(0, 'Elapsed Time', Exp_Data['Elapsed Time'])
		data_copy = data_copy.dropna()
		Exp_Data = Exp_Data.iloc[:2,:].append(data_copy)

		# Read in event times
		Exp_Events = pd.read_csv(event_location+Test_Name+'_Events.csv')
		Event_Times = []
		
		# convert event times from h:mm:ss to seconds
		for i in range(0,len(Exp_Events)):
			h, mm, ss = Exp_Events['Elapsed_Time'][i].split(':')
			converted_time = 3600*int(h)+60*int(mm)+int(ss)
			Event_Times.append(converted_time)

		# Get start and end times
		Start_Time = Event_Times[0]
		End_Time = Event_Times[-1]
		# Check if experiment data extend past end time
		if End_Time > len(Exp_Data.index.values):	# if no, set new end time to end of data
			End_Time = len(Exp_Data.index.values)
		else:	# if yes, cut off exp data to end time
			Exp_Data = Exp_Data.iloc[:End_Time, : ]

		# set time axis for plotting
		time = list(range(0, End_Time))
		area = 17.778

		for channels in [BDP1_channels,BDP4_channels]:			
			good_channels = []
			for channel in channels:
				if any([substring in channel for substring in skip_channels]):
					continue
				good_channels.append(channel)
				#Calculate velocity
				conv_inch_h2o = 0.04
				conv_pascal = 248.84
				convert_ftpm = 196.85
				end_zero_time = 45
				zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
				pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel]-zero_voltage)  # Convert voltage to pascals
				# Calculate flowrate
				Exp_Data[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (25+273.13)) * np.sign(pressure)

			# Calculate cfm
			CFM = area*np.mean(Exp_Data[good_channels],axis=1)
			zero_CFM = np.mean(CFM[0:end_zero_time])
			CFM = CFM - zero_CFM
			# if len(good_channels) == len(channels):
			# 	CFM_1 = area*(Exp_Data[channels[2]])
			# 	CFM_3 = area*np.mean(Exp_Data[channels[1:4]],axis=1)
			# 	zero_CFM_1 = np.mean(CFM_1[0:end_zero_time])
			# 	zero_CFM_3 = np.mean(CFM_3[0:end_zero_time])
			# 	CFM_1 = CFM_1 - zero_CFM_1
			# 	CFM_3 = CFM_3 - zero_CFM_3
			cfm_avgs = [0]

			# Calc avg CFM between events
			for i in range(1,len(Exp_Events)):
				cfm_avgs.append(np.mean(CFM[Event_Times[i-1]:Event_Times[i]]))

			# # save avg CFM to new event file
			# Exp_Events['CFM_Avg'] = cfm_avgs
			# Exp_Events.to_csv('../Experimental_Data/'+ Test_Name + '_Events_CFM.csv')

			fig = figure()
			plt.rc('axes')
			ax1 = plt.gca()
			plt.xlabel('Time (s)', fontsize=18)
			plt.ylabel('CFM (ft$^3$/min)', fontsize=18)
			ax1.set_xlim(0, End_Time)
			plt.xticks(fontsize=16)
			plt.yticks(fontsize=16)
			plt.plot(time,CFM,'r--',lw=1.5, label='CFM All')
			# if len(good_channels) == len(channels):
			# 	plt.plot(time,CFM_3,'b--',lw=1.5, label='CFM Middle 3')
			# 	plt.plot(time,CFM_1,'r-.',lw=1.5, label='CFM Middle')
			
			# plot avg lines between each event
			for i in range(1,len(Exp_Events)):
				plt.plot([Event_Times[i-1],Event_Times[i]],[cfm_avgs[i],cfm_avgs[i]],color='black',linewidth=2)
			
			ax1.yaxis.grid(which="major",color='0.75',lw=0.5,ls='--')
			plt.plot([0,End_Time-Start_Time],[0,0],color='k',ls='-',lw=0.75)
			handles1, labels1 = ax1.get_legend_handles_labels()
	
			# Add vertical lines and labels for timing information (if available)
			ax3 = ax1.twiny()
			ax1_xlims = ax1.axis()[0:2]
			ax3.set_xlim(ax1_xlims)
			# Remove NaN items from event timeline
			events = Exp_Events['Event']
			[plt.axvline(_x, color='0.5', lw=1) for _x in Event_Times]
			ax3.set_xticks(Event_Times)
			plt.setp(plt.xticks()[1], rotation=40)
			ax3.set_xticklabels(events.values, fontsize=8, ha='left')
			plt.xlim([0, End_Time])
			# Set figure size
			fig.set_size_inches(10,8)

			plt.legend(handles1, labels1, loc='upper right', fontsize=10, handlelength=3)
			savefig(chart_location+Test_Name+'_CFM_'+channel[:4]+'.pdf')
			close()

		#-----------------------
		# One off bar plots example
		#-----------------------
		# exp04 = pd.read_csv('../Experimental_Data/Exp_04_102615_Events_CFM.csv')
		# exp08 = pd.read_csv('../Experimental_Data/Exp_08_102615_Events_CFM.csv')

		# mean_values = [exp08['CFM_Avg'][1],exp04['CFM_Avg'][1],exp04['CFM_Avg'][5]]
		# variance = [0.18*exp08['CFM_Avg'][1],0.18*exp04['CFM_Avg'][1],0.18*exp04['CFM_Avg'][5]]
		# bar_labels = [exp08['Event'][1],exp04['Event'][1],exp04['Event'][5]]
		# x_pos = list(range(len(bar_labels)))
		# fig, ax = plt.subplots(figsize=(10, 9))
		# plt.bar(x_pos, mean_values, yerr=variance, align='center', color=tableau20[0],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
		# max_y = max(zip(mean_values, variance))
		# plt.ylim([0, (max_y[0] + max_y[1]) * 1.1])
		# plt.ylabel('Average CFM (ft$^3$/min)', fontsize=18)
		# plt.xticks(x_pos, bar_labels,rotation = -15)
		# ax.tick_params(axis='both', which='major', labelsize=16)
		# plt.legend(['150 gpm @ 50 psi'], loc='upper left')
		# savefig(chart_location+'Hosestream_Type_1_5_int'+'.pdf')
