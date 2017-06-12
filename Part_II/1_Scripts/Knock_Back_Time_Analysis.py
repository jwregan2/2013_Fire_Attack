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
import matplotlib as mpl 
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
data_location = '../2_Data/'
info_location = '../3_Info/'
output_location = '../0_Images/Script_Figures/Knock_Back/'
# Create output location if doesn't exist
if not os.path.exists(output_location):
	os.makedirs(output_location)

# Load experiment dicts
all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))
all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))
all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))
all_channels = pd.read_csv(info_location + 'Channels.csv').set_index('Channel')

# Read in description of experiments & make list of channels to skip for each experiment
channels_to_skip = {}
Exp_Des = pd.read_csv(info_location + 'Description_of_Experiments.csv').set_index('Experiment')
for exp in Exp_Des.index.values:
	channels_to_skip[exp] = Exp_Des['Excluded Channels'][exp].split('|')

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
sensor_groups = np.array([ ['Bedroom_1_Temps'],
						   ['Bedroom_1_Temps'], 
						   ['Bedroom_1_Temps'],
						   ['Bedroom_1_Temps'],
						   ['Bedroom_1_Temps','End_Hall_Temps','Bedroom_2_Temps','Bedroom_4_Temps'] ])

skip_TCs = [6,4,2]

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

# List of markers for plots & frequency of marker on plot
markers = ['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H']

# Loop through experiments in each comparison set
set_idx = 0 	# variable used to ID each comparison set of experiments
for Exp_Set in comparison_sets:
	extinguish_event_idx = event_row_nums[set_idx]-1
	if set_idx==4:
		mark_freq = 10
		xaxis_lim = 95
		x_ticks = [0,15,30,45,60,75,90]
	else:
		mark_freq = 5
		xaxis_lim = 60
		x_ticks = [0,10,20,30,40,50]
	print('----- Comparing Experiments from set',Exp_Set,' -----')
	for Exp_Num in Exp_Set:
		# Define experiment number, test name, and data file name
		Exp_Num = str(Exp_Num)
		Test_Name = 'Experiment_'+Exp_Num
		File_Name = Test_Name+'_Data'

		# Read in experimental data, flow data, & event times for experiment
		Exp_Data = all_exp_data[File_Name]
		Exp_Flow_Data = all_flow_data[File_Name]
		Events = all_exp_events[Test_Name+'_Events']

		print('Loaded data and event files for '+Test_Name)

		# Grab event times & labels (if applicable)
		start_df_idx = Events['Time_Seconds'].iloc[extinguish_event_idx]
		end_df_idx = start_df_idx+xaxis_lim
		# if set_idx >= 3: # Multiple events for comparison between Exp 22 and 24
		event_times = []
		event_labels = []
		for index,row in Events.iloc[extinguish_event_idx:-1,:].iterrows():
			time = row['Time_Seconds']
			if time-start_df_idx < xaxis_lim:
				event_times.append(time)
				event = index
				if event == 'Suppression BR1 Window Solid Stream':
					event_labels.append('Suppr. BR1 Window Solid')
				elif event == 'Exterior Suppression BR1 Window Solid Stream':
					event_labels.append('Suppr. BR1 Window Solid')
				elif event == 'Exterior Suppression BR1 Window Straight Stream':
					event_labels.append('Suppr. BR1 Window Straight')
				elif event == 'Exterior Suppression BR2 Window Straight Stream':
					event_labels.append('Suppr. BR2 Window Straight')
				else:
					event_labels.append(event)
			else:
				continue

		# Create df of flow data to plot
		flow_data = Exp_Flow_Data[:].loc[start_df_idx:end_df_idx]
		# set index to match plot's time axis
		flow_data['Plot Time'] = flow_data.index.values - start_df_idx
		flow_data = flow_data.set_index('Plot Time')
			
		# Iterate through sensor groups for each comparison set
		for group in sensor_groups[set_idx]:

			# Get list of channel names
			channel_names = all_channels[all_channels['Primary_Chart']==group].index.values

			# Make df of channel data
			group_data = Exp_Data[channel_names].loc[start_df_idx-6:end_df_idx]

			# Print 'Plotting Chart XX'
			print ('Plotting '+group.replace('_',' ')+' for '+Test_Name)

			# Create figure to plot temperatures
			fig = plt.figure()
			mpl.rcParams['axes.prop_cycle'] = cycler(color=tableau20[2:]) # ignore first two colors (blue shade used on plots)
			plot_markers = cycle(markers)

			ax1 = plt.gca()
			ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
			ax1_xlims = ax1.axis()[0:2]
			plt.ylim([0, 1800])
			plt.grid(True)
			plt.xlabel('Time (sec)', fontsize=48)
			plt.xticks(x_ticks, fontsize=44)
			plt.yticks(fontsize=44)

			# Shade blue areas on plot when flow occurs
			plt.fill_between(flow_data.index.values, 0, 1800, where=flow_data['GPM']>10, facecolor='blue', alpha=0.3)

			# Plot flow data on secondary axis & set axis label/ticks
			ax2 = ax1.twinx()
			plt.plot(flow_data.index.values, flow_data['Total Gallons'], lw=6, color='#1f77b4')
			ax2.set_ylim(0,200)
			ax2.set_ylabel('Total Flow (Gallons)', fontsize=48)
			ax2.tick_params(labelsize=44)

			# Iterate through sensor group channels
			for channel in channel_names:
				# Skip plot quantity if channel name is blank
				if pd.isnull(channel):
					continue

				if int(channel[-1]) in skip_TCs:	# only plot TC 7, 5, 3, & 1
					continue

	   			# Skip excluded channels listed in test description file
				if channel in channels_to_skip[File_Name]:
					continue
				
				# Define channel data and time
				current_data = group_data[channel]

				# Plot channel data
				ax1.plot(group_data[channel].index.values-start_df_idx, current_data, lw=4,
					marker=next(plot_markers), markevery=int(mark_freq),
					mew=3, mec='none', ms=20, label=all_channels['Title'][channel])

			plt.xlim([-6, xaxis_lim])

			ax1.set_zorder(ax2.get_zorder()+1) # put ax in front of ax2 
			ax1.patch.set_visible(False) # hide the 'canvas' 

			# Secondary x-axis for event info
			ax3=ax1.twiny()
			ax3.set_zorder(ax1.get_zorder())
			ax3.set_xlim([-6, xaxis_lim])
			[ax3.axvline((idx-start_df_idx),color='0',lw=4) for idx in event_times]
			ax3.set_xticks([(idx-start_df_idx) for idx in event_times])
			plt.setp(plt.xticks()[1], rotation=45)		
			ax3.set_xticklabels([label for label in event_labels], fontsize=30, ha='left')

			fig.set_size_inches(20, 18)
			
			# Set y-label to degrees F with LaTeX syntax
			ax1.set_ylim(100,1800)
			ax1.set_ylabel('Temperature ($^\circ$F)', fontsize=48)

			handles1, labels1 = ax1.get_legend_handles_labels()
			plt.legend(handles1, labels1, loc='upper right', fontsize=40, handlelength=3, labelspacing=.15)

			plt.tight_layout()
			
			# Save plot to file
			if set_idx == 4: 	# used for Exp 22/24 comparison containing multiple events
				plt.savefig(output_location+Test_Name+'_'+group+'_full.pdf') 
			else:
				plt.savefig(output_location+Test_Name+'_'+group+'.pdf')
			
			plt.close('all')
		print()

	set_idx = set_idx+1
   