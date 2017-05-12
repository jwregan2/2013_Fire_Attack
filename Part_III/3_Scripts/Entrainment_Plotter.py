import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
from dateutil.relativedelta import relativedelta
from itertools import cycle

# Set file locations

data_location = '../0_Data/Ent_Experiment_Data/CSV/'
event_location = '../1_Info/Ent/Events/'
chart_location = '../2_Plots/Flow_Plots/'

# info_file = '../Info/description_of_experiments_entrainment.csv'
# plot_file = '../Info/description_of_charts.csv'

# Read in description of experiments
# Exp_Des = pd.read_csv(info_file)
# Exp_Des = Exp_Des.set_index('Test_Name')
# Set files to skip in experimental directory
skip_files = ['_events']

channels = ['BDP11V','BDP12V','BDP13V','BDP14V','BDP15V']

# Loop through Experiment files
for f in os.listdir(data_location):
	if f.endswith('.csv'):

		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue

		# Read in experiment file
		File_Name = f[:-4]

		# Get experiment name from file
		Test_Name = File_Name[:-5]
		Exp_Num = Test_Name[11:]

		# exp = experiment[11:-9]
		Exp_Data = pd.read_csv(data_location + f)
		data_copy = Exp_Data.drop('Elapsed Time', axis=1)
		data_copy = data_copy.rolling(window=5, center=True).mean()
		data_copy.insert(0, 'Elapsed Time', Exp_Data['Elapsed Time'])
		data_copy = data_copy.dropna()
		Exp_Data = data_copy

		Exp_Events = pd.read_csv(event_location+Test_Name+'_Events.csv')
		Event_Time = [datetime.datetime.strptime(t, '%Y-%m-%d-%H:%M:%S') for t in Exp_Events['Time']]

		# if Exp_Des['Test_Config'][Test_Name] == 'ignore':
		# 	continue

		# temp_time = []
		# for i in range(len(Exp_Data)):
		# 	temp_time.append(Event_Time[i].timestamp() - Event_Time[0].timestamp())
		# Exp_Events['Elapsed_Time'] = temp_time
		Start_Time = 0
		End_Time = len(Exp_Data)

		print (Test_Name)

		area = 17.778
		for channel in channels:
			#Calculate velocity
			conv_inch_h2o = 0.04
			conv_pascal = 248.84
			convert_ftpm = 196.85
			end_zero_time = 30
			zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
			pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel]-zero_voltage)  # Convert voltage to pascals
			# Calculate flowrate
			Exp_Data[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (25+273.13)) * np.sign(pressure)

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
		cfm_avgs = [0]
		event_times_sec = []
		# Grab hh:mm:ss from event file and calc avg CFM between events
		for i in range(1,len(Exp_Events)):
			pos2_hr, pos2_min, pos2_sec = Exp_Events['Elapsed_Time'][i].split(':')
			pos1_hr, pos1_min, pos1_sec = Exp_Events['Elapsed_Time'][i-1].split(':')
			pos2 = 3600*int(pos2_hr)+60*int(pos2_min)+int(pos2_sec)
			pos1 = 3600*int(pos1_hr)+60*int(pos1_min)+int(pos1_sec)
			cfm_avgs.append(np.mean(CFM[pos1:pos2]))
			event_times_sec.append(pos1)
		event_times_sec.append(pos2)

		# # save avg CFM to new event file
		# Exp_Events['CFM_Avg'] = cfm_avgs
		# Exp_Events.to_csv('../Experimental_Data/'+ Test_Name + '_Events_CFM.csv')
		time = list(range(len(Exp_Data)))

		fig = figure()
		plt.plot(time,CFM,'r--',linewidth=1.5)
		plt.plot(time,CFM_3,'b--',label='CFM Middle 3')
		plt.plot(time,CFM_1,'r-.',label='CFM Middle')
		for i in range(1,len(Exp_Events)):
			plt.plot([event_times_sec[i-1],event_times_sec[i]],[cfm_avgs[i],cfm_avgs[i]],color='black',linewidth=2)
		ax1 = plt.gca()
		handles1, labels1 = ax1.get_legend_handles_labels()
		ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
		ax1_xlims = ax1.axis()[0:2]
		plt.xlim([0, End_Time-Start_Time])
		plt.xlabel('Time (s)')
		plt.ylabel('CFM (ft$^3$/min)')
		try:
			# Add vertical lines and labels for timing information (if available)
			ax3 = ax1.twiny()
			ax3.set_xlim(ax1_xlims)
			# Remove NaN items from event timeline
			events = Exp_Events['Event']
			[plt.axvline(_x, color='0.50', lw=1) for _x in event_times_sec]
			ax3.set_xticks(event_times_sec)
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

