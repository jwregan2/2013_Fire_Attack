# ******************************** Run notes ***********************************
# Script used to compare knock back time for various experiments, specifically:
# 	INTERIOR:
# 		Compare 2, 7, 13 (Flow and move SB)
# 		Compare 6, 8, 14 (Shutdown and move SB)
# 		Compare 11, 16 (flow and move Fog)
# 	EXTERIOR:
# 		Compare 18, 20, (just initial hit) vs. 22, 24 (just bedroom 1)
# 		Compare 22 (BD1 and interior) vs. 24 (BD1, BD2, and Interior)		
# 
# Currently, script set up to generate plots of Bedroom 1 temperature data
# 	over duration from 6 seconds before start of suppression to 60 seconds after 
# 	start of suppression
#

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

# Define filter for low pass filtering of pressure/temperature for BDP
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filtfilt(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Set file locations
data_location = '../2_Data/Smaller_Data/'

channel_location = '../3_Info/'

output_location = '../0_Images/Script_Figures/Knock_Back/'

info_file = '../3_Info/Description_of_Experiments.csv'

# Read in channel list
channel_list = pd.read_csv(channel_location+'Channels.csv')

# Set index value for channels as 'Channel'
channel_list = channel_list.set_index('Channel')

# Create groups data by grouping channels for 'Chart'
channel_groups = channel_list.groupby('Primary_Chart')
# channel_groups = channel_list.groupby('Secondary_Chart')

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)

# Set index of description of experiments to Experiment
Exp_Des = Exp_Des.set_index('Experiment')

# Set files to skip in experimental directory
skip_files = ['example']

# Create numpy array containing desired experiment sets to compare; 
# 	each array corresponds to a comparison set
comparison_sets = np.array([ [2,7,13],
							 [6,8,14],
							 [11,16],
							 [18,20,22,24] ])
#,[22,24] ])

# List of suppression event row number in event time file for each comparison set
event_row_nums = [5,5,5,2]

# Create numpy array with sensors to be used for analysis of each 
# 	comparison set (i.e., each array in comparison_sets)
sensor_groups = np.array([ ['End_Hall_Temps','Middle_Hall_Temps','Victim_1_Temps','Victim_3_Temps','Bedroom_1_Temps'],
						   ['End_Hall_Temps','Middle_Hall_Temps','Victim_1_Temps','Bedroom_1_Temps'], 
						   ['End_Hall_Temps','Middle_Hall_Temps','Start_Hall_Temps','Victim_1_Temps','Victim_3_Temps','Bedroom_1_Temps'],
						   ['Bedroom_1_Temps'] ])

# Define 20 color pallet using RGB values
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Define RGB values in pallet 
for i in range(len(tableau20)):
	r, g, b = tableau20[i]
	tableau20[i] = (r / 255., g / 255., b / 255.)

markers = ['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H']

# Loop through experiments in each comparison set
set_idx = 0 	# variable used to ID each comparison set of experiments
for Exp_Set in comparison_sets:
	extinguish_event_index = event_row_nums[set_idx]-1
	print('--- Comparing Experiments from set',Exp_Set,' ---')
	knock_back_time_df = pd.DataFrame(sensor_groups[set_idx],columns=['Sensor Group'])
	for Exp_Num in Exp_Set:
		# Define experiment number, test name, and data file name
		Exp_Num = str(Exp_Num)
		Test_Name = 'Experiment_'+Exp_Num
		File_Name = Test_Name+'_Data'

		# Read in experimental data
		Exp_Data = pd.read_csv(data_location+File_Name+'.csv')

		# Get house & data speed
		House = Exp_Des.loc[File_Name, 'House']
		Speed = Exp_Des.loc[File_Name, 'Speed']

		# Read in event file for given test and set event column as index
		Events = pd.read_csv(channel_location+'Events/'+Test_Name+'_Events.csv', index_col='Event')

		print('Loaded data and event files for '+Test_Name)

		extinguish_time = Events['Time'].iloc[extinguish_event_index] 	# event time listed in form h:mm:ss
		
		# Uncomment to print times in order to verify they are correct
		# print('Check Times:')
		# print('    Extinguish time = '+str(extinguish_time))

		# If statements to determine whether or not data is in high speed and assigning time accordingly based on data csv file
		if Speed == 'low':
			if Exp_Num == '6' or Exp_Num == '18':	
				data_per_sec = 0.5		# Data collected every other second 
				extinguish_idx = Exp_Data[Exp_Data['Elapsed Time']=='0'+extinguish_time].index.tolist()[0] 		# timestamp of form hh:mm:ss				
			else:
				data_per_sec = 1 	# Data collected every second
				extinguish_idx = Exp_Data[Exp_Data['Elapsed Time']==extinguish_time].index.tolist()[0]
		elif Speed == 'high':
			data_per_sec = 10 	# Data collected every 0.1 second
			extinguish_idx = Exp_Data[Exp_Data['Elapsed Time']==extinguish_time[2:]+'.0'].index.tolist()[0]
		else:
			print('[ERROR!]: data speed not set properly!')
			print(' 	Speed = '+Speed)
			exit()

		# Get start/end index for data to plot
		start_df_idx = int(extinguish_idx-data_per_sec*6)
		end_df_idx = int(extinguish_idx+data_per_sec*60)
		
		# Uncomment to print times in order to verify they are correct
		# print('    Extinguish time = '+str(Exp_Data['Elapsed Time'].iloc[extinguish_idx]))
		# print('    Extinguish index = '+str(extinguish_idx))
		# print('    Start dataframe at '+str(Exp_Data['Elapsed Time'].iloc[start_df_idx]))
		# print('    End dataframe at '+str(Exp_Data['Elapsed Time'].iloc[end_df_idx]))
		# print()

		if House == 'a':
			scalefactor = 'ScaleFactor_A'
			Transport_Time = 'Transport_Time_A'
		elif House == 'b':
			scalefactor = 'ScaleFactor_B'
			Transport_Time = 'Transport_Time_B'
		else:
			print('[ERROR!]: House label not set properly!')
			print(' 	House = '+House)
			exit()

		# # Original criteria analysis based on (T_max-T_min)
		# delta_T_col = []
		# knock_back_time_col = []
		# for group in sensor_groups[set_idx]:
		# 	channel_names = channel_groups.get_group(group).index.values
		# 	group_data = Exp_Data[channel_names][extinguish_idx-data_per_sec+1:]
		# 	initial_temps = np.mean(group_data[:].iloc[:data_per_sec])		
		# 	count = 0
		# 	entireloop = True
		# 	for index,row in group_data.iterrows():
		# 		count = count + 1
		# 		if count != data_per_sec:
		# 			continue
		# 		else:
		# 			count = 0
		# 			sec_values = np.mean(group_data[:].loc[-data_per_sec+1+index:index])
		# 			max_T = max(sec_values)
		# 			min_T = min(sec_values)
		# 			if (max_T-min_T) < 30 and max_T < 100:
		# 				avg_next_5s = np.mean(group_data[:].iloc[index-extinguish_idx:index-extinguish_idx+5*data_per_sec])
		# 				max_avg = max(avg_next_5s)
		# 				min_avg = min(avg_next_5s)
		# 				if max_avg-min_avg < 30:
		# 					delta_Ts = initial_temps-sec_values
		# 					delta_T_col.append(max(delta_Ts)) 
		# 					knock_back_time_col.append((index-extinguish_idx)/data_per_sec)
		# 					entireloop = False						
		# 					break
			
		# 	if entireloop: 	# Criteria never met; enter placeholder numbers for df
		# 		delta_T_col.append(100000)
		# 		knock_back_time_col.append(100000)

		# knock_back_time_df['Exp. '+Exp_Num+' Delta T'] = delta_T_col
		# knock_back_time_df['Exp. '+Exp_Num+' Knock Back Time'] = knock_back_time_col

		delta_T_col = []
		knock_back_time_col = []

		# Set marker frequency based on sampling rate
		mark_freq = 10*data_per_sec

		# Iterate through sensor groups for each comparison set
		for group in sensor_groups[set_idx]:
			# Only consider bedroom 1 temps for now
			if group != 'Bedroom_1_Temps':
				continue

			# Get list of channel names
			channel_names = channel_groups.get_group(group).index.values

			# Make dataframe of channels from 5 seconds before extinguishment to 60 seconds after
			group_data = Exp_Data[channel_names][start_df_idx:end_df_idx+1]

			# Create figure to plot temperatures
			fig = plt.figure()
			plt.rc('axes', color_cycle=tableau20)
			plot_markers = cycle(markers)

			# Print 'Plotting Chart XX'
			print ('Plotting '+group.replace('_',' ')+' for '+Test_Name)
			print()

			# Iterate through sensor group channels
			for channel in channel_names:
				# Skip plot quantity if channel name is blank
				if pd.isnull(channel):
					continue

	   			# Skip excluded channels listed in test description file
				if any([substring in channel for substring in Exp_Des['Excluded Channels'][File_Name].split('|')]):
					continue

	            # Set scale factor and offset
				scale_factor = channel_list[scalefactor][channel]
				offset = channel_list['Offset'][channel]
				
				# Define channel data and time
				current_data = group_data[channel]
				end_time = (len(current_data)/data_per_sec)-6
				range_spacing = 1./data_per_sec

				time = np.arange(-6,end_time,range_spacing)
				
				# Set data to include slope and intercept
				current_data = current_data * scale_factor + offset

				# Plot channel data
				plt.plot(time, current_data, lw=1.5,
					marker=next(plot_markers), markevery=int(mark_freq),
					mew=3, mec='none', ms=7, label=channel_list['Title'][channel])

			# Set y-label to degrees F with LaTeX syntax
			plt.ylabel('Temperature ($^\circ$F)', fontsize=20)

			# Set secondary y-axis label to degrees C
			secondary_axis_label = 'Temperature ($^\circ$C)'
			
			# Set scaling dependent on axis scale defined above
			secondary_axis_scale = 2000. * 5/9 - 32

            # Set axis options, legend, tickmarks, etc.
			ax1 = plt.gca()
			handles1, labels1 = ax1.get_legend_handles_labels()
			plt.xlim([-6, end_time-1])
			ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
			ax1_xlims = ax1.axis()[0:2]
			plt.xticks(fontsize=16)
			plt.yticks(fontsize=16)
			plt.grid(True)
			plt.xlabel('Time (sec)', fontsize=20)

			# Secondary y-axis parameters
			# ax2 = ax1.twinx()
			# ax2.set_ylabel(secondary_axis_label, fontsize=32)
			# plt.xticks(fontsize=28)
			# plt.yticks(fontsize=28)
			# ax2.set_ylim([0, secondary_axis_scale])

			# Secondary x-axis for event info
			ax3=ax1.twiny()
			ax3.set_xlim(-6,end_time)
			plt.axvline(0,color='0',lw=2) 
			ax3.set_xticks([0])
			plt.setp(plt.xticks()[1], rotation=60)		
			ax3.set_xticklabels(['Start Suppression'], fontsize=10, ha='left')
			fig.set_size_inches(9, 8)
			plt.tight_layout()
			
			plt.legend(handles1, labels1, loc='upper right', fontsize=10, handlelength=3)

	        # Save plot to file
			plt.savefig(output_location+Test_Name+'_'+group+'.pdf')
			plt.close('all')

			# # Store initial temperatures at start of extinguishment
			# initial_temps = np.mean(group_data[:].iloc[data_per_sec*5-data_per_sec+1:data_per_sec*5+1])
			# print('Check initial temperatures calculated over correct range:')
			# print(group_data[:].iloc[data_per_sec*5-data_per_sec+1:data_per_sec*5+1])
			# print()

			# count = 0
			# entireloop = True
			# for index,row in group_data.iterrows():
			# 	count = count + 1
			# 	if count != data_per_sec:
			# 		continue
			# 	else:
			# 		count = 0
			# 		sec_values = np.mean(group_data[:].loc[-data_per_sec+1+index:index])
			# 		max_T = max(sec_values)
			# 		min_T = min(sec_values)
			# 		if (max_T-min_T) < 30 and max_T < 100:
			# 			avg_next_5s = np.mean(group_data[:].iloc[index-extinguish_idx:index-extinguish_idx+5*data_per_sec])
			# 			max_avg = max(avg_next_5s)
			# 			min_avg = min(avg_next_5s)
			# 			if max_avg-min_avg < 30:
			# 				delta_Ts = initial_temps-sec_values
			# 				delta_T_col.append(max(delta_Ts)) 
			# 				knock_back_time_col.append((index-extinguish_idx)/data_per_sec)
			# 				entireloop = False						
			# 				break

	# 	knock_back_time_df['Exp. '+Exp_Num+' Delta T'] = delta_T_col
	# 	knock_back_time_df['Exp. '+Exp_Num+' Knock Back Time'] = knock_back_time_col


	# knock_back_time_df = knock_back_time_df.set_index('Sensor Group')
	# print(knock_back_time_df)
	# print()
	set_idx = set_idx+1
   