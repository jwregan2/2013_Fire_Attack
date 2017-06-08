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
import pickle
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

# Load flow data from dictionary using pickle
all_flow_data = pickle.load(open('../2_Data/all_flow_data.dict', 'rb'))

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
							 [18,20,22,24],
							 [22,24] ])

# List of suppression event row number in event time file for each comparison set
event_row_nums = [5,5,5,2,2]

# Create numpy array with sensors to be used for analysis of each 
# 	comparison set (i.e., each array in comparison_sets)
# sensor_groups = np.array([ ['End_Hall_Temps','Middle_Hall_Temps','Victim_1_Temps','Victim_3_Temps','Bedroom_1_Temps'],
# 						   ['End_Hall_Temps','Middle_Hall_Temps','Victim_1_Temps','Bedroom_1_Temps'], 
# 						   ['End_Hall_Temps','Middle_Hall_Temps','Start_Hall_Temps','Victim_1_Temps','Victim_3_Temps','Bedroom_1_Temps'],
# 						   ['Bedroom_1_Temps'],
# 						   ['Bedroom_1_Temps','End_Hall_Temps','Bedroom_2_Temps','Bedroom_4_Temps'] ])

sensor_groups = np.array([ ['Bedroom_1_Temps'],
						   ['Bedroom_1_Temps'], 
						   ['Bedroom_1_Temps'],
						   ['Bedroom_1_Temps'],
						   ['Bedroom_1_Temps','End_Hall_Temps','Bedroom_2_Temps','Bedroom_4_Temps'] ])

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
###### Skip plotting flow for plots with multiple events until others sets plotted with flow	
	if set_idx == 4:
		continue
	extinguish_event_idx = event_row_nums[set_idx]-1
	print('--- Comparing Experiments from set',Exp_Set,' ---')
	knock_back_time_df = pd.DataFrame(sensor_groups[set_idx],columns=['Sensor Group'])
	for Exp_Num in Exp_Set:
		# Define experiment number, test name, and data file name
		Exp_Num = str(Exp_Num)
		Test_Name = 'Experiment_'+Exp_Num
		File_Name = Test_Name+'_Data'

		# Read in experimental data and flow data
		Exp_Data = pd.read_csv(data_location+File_Name+'.csv')
		Exp_Flow_Data = all_flow_data[File_Name]

		# Get house & data speed
		House = Exp_Des.loc[File_Name, 'House']
		Speed = Exp_Des.loc[File_Name, 'Speed']

		# Read in event file for given test and set event column as index
		Events = pd.read_csv(channel_location+'Events/'+Test_Name+'_Events.csv', index_col='Event')

		print('Loaded data and event files for '+Test_Name)

		if set_idx == 4: # Multiple events for comparison between Exp 22 and 24	
			event_times = Events['Time'].iloc[extinguish_event_idx:-1]
			event_labels = Events.index.values.astype(str)[extinguish_event_idx:-1]
			extinguish_time = event_times[0]
		else:
			extinguish_time = Events['Time'].iloc[extinguish_event_idx] 	# event time listed in form h:mm:ss

		start_flow_idx = float(extinguish_time[-5:-3])*60+float(extinguish_time[-2:]) - 6.0
		end_flow_idx = float(extinguish_time[-5:-3])*60+float(extinguish_time[-2:])+60.1

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
				if set_idx == 4: 	# Get index for each event so they can be marked on plot
					event_idxs = []
					for timestamp in event_times:
						event_idxs.append(Exp_Data[Exp_Data['Elapsed Time']==timestamp].index.tolist()[0])
		elif Speed == 'high':
			data_per_sec = 10 	# Data collected every 0.1 second
			extinguish_idx = Exp_Data[Exp_Data['Elapsed Time']==extinguish_time[2:]+'.0'].index.tolist()[0]
			if set_idx == 4: 	# Get index for each event so they can be marked on plot
				event_idxs = []
				for timestamp in event_times:
					event_idxs.append(Exp_Data[Exp_Data['Elapsed Time']==timestamp[2:]+'.0'].index.tolist()[0])
		else:
			print('[ERROR!]: data speed not set properly!')
			print(' 	Speed = '+Speed)
			exit()

		# Get start/end index for data to plot
		if set_idx == 4: 	# Different range for comparison between Exp 22 and 24
			start_df_idx = int(extinguish_idx-data_per_sec*6)
			end_df_idx = int(event_idxs[-1]+data_per_sec*60)			
		else:
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

		delta_T_col = []
		knock_back_time_col = []

		# Set marker frequency based on sampling rate
		mark_freq = 10*data_per_sec

##### MAKE DF FOR FLOW DATA ALONG EVENT RANGE; CHECK SAMPLE RATE IN FLOW DATA FILES
		flow_data = Exp_Flow_Data[:].loc[start_flow_idx:end_flow_idx]
		flow_times = flow_data.index.values - start_flow_idx - 6.0

		# Iterate through sensor groups for each comparison set
		for group in sensor_groups[set_idx]:

			# Get list of channel names
			channel_names = channel_groups.get_group(group).index.values

			# Make dataframe of channels from 6 seconds before extinguishment to 60 seconds after
			group_data = Exp_Data[channel_names][start_df_idx:end_df_idx+1]

			# Print 'Plotting Chart XX'
			print ('Plotting '+group.replace('_',' ')+' for '+Test_Name)

			# Create figure to plot temperatures
			fig = plt.figure()
			plt.rc('axes', prop_cycle=(cycler('color',tableau20[2:]))) # ignore first two colors (blue shade used on plots)
			plot_markers = cycle(markers)

			ax1 = plt.gca()
			ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
			ax1_xlims = ax1.axis()[0:2]
			plt.ylim([0, 1600])
			plt.grid(True)
			plt.xlabel('Time (sec)', fontsize=48)
			plt.xticks(fontsize=44)
			plt.yticks(fontsize=44)

			# Plot flow data on secondary axis & set axis label/ticks
			ax2 = ax1.twinx()
			ax2.plot(flow_times, flow_data['Total Gallons'], lw=6, color='#1f77b4',)
			ax2.set_ylim(0,400)
			ax2.set_ylabel('Total Flow (Gallons)', fontsize=48)
			ax2.tick_params(axis='y', labelsize=44)

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
				ax1.plot(time, current_data, lw=4,
					marker=next(plot_markers), markevery=int(mark_freq),
					mew=3, mec='none', ms=12, label=channel_list['Title'][channel])

			plt.xlim([-6, 60])
			fig.set_size_inches(20, 18)

			# Set y-label to degrees F with LaTeX syntax
			ax1.set_ylim(150,1600)
			ax1.set_ylabel('Temperature ($^\circ$F)', fontsize=48)

			plt.subplots_adjust(top=0.8)

			# # Secondary x-axis for event info
			# ax3=ax1.twiny()
			# ax3.set_xlim(-6,end_time-1)
			# if set_idx == 4: 	# Multiple events for Exp 22 and 24 comparison
			# 	[plt.axvline((idx-extinguish_idx)/data_per_sec,color='0',lw=2) for idx in event_idxs]
			# 	ax3.set_xticks([(idx-extinguish_idx)/data_per_sec for idx in event_idxs])
			# 	plt.setp(plt.xticks()[1], rotation=45)		
			# 	ax3.set_xticklabels([label for label in event_labels], fontsize=10, ha='left')
			# 	fig.set_size_inches(8, 8)
			# else:
			# 	plt.axvline(0,color='0',lw=2) 
			# 	ax3.set_xticks([0])
			# 	plt.setp(plt.xticks()[1], rotation=45)		
			# 	ax3.set_xticklabels(['Start Suppression'], fontsize=10, ha='left')
			# 	fig.set_size_inches(9, 5)
			# plt.tight_layout()

			handles1, labels1 = ax1.get_legend_handles_labels()
			ax1.legend(handles1, labels1, loc='upper right', fontsize=40, handlelength=3, labelspacing=.15)
			plt.subplots_adjust(top=.9)

			if not os.path.exists(output_location):
				os.makedirs(output_location)

			# Save plot to file
			if set_idx == 4:
				plt.savefig(output_location+Test_Name+'_'+group+'_full.pdf')
			else:
				plt.savefig(output_location+Test_Name+'_'+group+'.pdf')
			
			plt.close('all')
		print()

	set_idx = set_idx+1
   