# ******************************** Run notes ***********************************
# Script used to generate plots for Section 5.5 Impact of "Whip" on Regrowth:
# 	
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

# Set file locations
data_location = '../2_Data/'
info_location = '../3_Info/'
output_location = '../0_Images/Script_Figures/Whip_Regrowth/'
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
comparison_sets = np.array([ [18,20], 
							 [24,24,27] ])

# List of suppression event row number in event time file for each comparison set
event_row_nums = np.array([ [2,2],
							[2,3,3] ])

# Whip type used during each experiment; will use for event callout
whip_types = np.array([ ['None','Solid, Half Bale Whip'],
					 	['Narrow Fog Whip','Narrow Fog Whip','None'] ])

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
	# Set whip labels for comparison set
	whip_labels = cycle(whip_types[set_idx])
	event_rows = cycle(event_row_nums[set_idx])

	print('----- Comparing Experiments from set',Exp_Set,' -----')
	for Exp_Num in Exp_Set:
		# Define experiment number, test name, & data file name
		Exp_Num = str(Exp_Num)
		Test_Name = 'Experiment_'+Exp_Num
		File_Name = Test_Name+'_Data'

		# Read in experimental data, flow data, & event times for experiment
		Exp_Data = all_exp_data[File_Name]
		Exp_Flow_Data = all_flow_data[File_Name]
		Events = all_exp_events[Test_Name+'_Events']

		print('Loaded data and event files for '+Test_Name)

		# Determine extinguish event row number index
		extinguish_event_idx = next(event_rows)-1

		# Store whip type for experiment
		whip_label = next(whip_labels)

		# Save suppression event time & end plot time (according to data time)
		start_df_idx = Events['Time_Seconds'].iloc[extinguish_event_idx]
		end_df_idx = Events['Time_Seconds'].iloc[-2]+10

		# Initialize event callout & time lists with initial event label & time at t = 0 s
		event_labels = []
		event_times = []
		for event in Events.index.values[extinguish_event_idx:-1]:
			if event == 'Suppression BR1 Window Solid Stream':
				event_labels.append('Suppr. BR1 Window Solid')
			elif event == 'Exterior Suppression BR1 Window Solid Stream':
				event_labels.append('Suppr. BR1 Window Solid')
			elif event == 'Exterior Suppression BR1 Window Straight Stream':
				event_labels.append('Suppr. BR1 Window Straight')
			elif event == 'Exterior Suppression BR2 Window Straight Stream':
				event_labels.append('Suppr. BR2 Window Straight')
			elif event == 'Exterior Suppression BR1 Window Narrow Fog':
				event_labels.append('Suppr. BR1 Window Narrow Fog')
			elif event == 'Exterior Suppression BR4 Window Straight Stream':
				event_labels.append('Suppr. BR4 Window Straight')
			else:
				event_labels.append(event)

			event_times.append(Events.loc[event, 'Time_Seconds']-start_df_idx)

		# Create df of flow data to plot
		flow_data = Exp_Flow_Data[:].loc[start_df_idx:end_df_idx]

		# set index to match plot's time axis
		flow_data['Plot Time'] = flow_data.index.values - start_df_idx
		flow_data = flow_data.set_index('Plot Time')

		# Add whip event label & time to lists (if applicable)
		if whip_label != 'None':
			# Determine when switch to whip occurs
			flowing = True
			idx = 29
			for GPM in flow_data['GPM'].iloc[30:]:
				idx += 1
				if flowing:
					if GPM > 20:
						continue
					else:
						# Check values at 0.2 & 0.4 sec later to verify nozzle off
						if GPM > flow_data['GPM'].iloc[idx+2] and flow_data['GPM'].iloc[idx+2] > flow_data['GPM'].iloc[idx+4]:
							flowing = False
				else:
					if GPM > 20:
						# Check values at 0.2 & 0.4 sec later to verify nozzle flowing
						if GPM < flow_data['GPM'].iloc[idx+2] and flow_data['GPM'].iloc[idx+2] < flow_data['GPM'].iloc[idx+4]:
							whip_time = flow_data.index.values[idx]
							break

			# Add whip label & time to lists
			event_labels.insert(1, whip_label)
			event_times.insert(1, whip_time)

		# Determine sensor group to plot
		if Exp_Num != '24':
			if Exp_Num=='27':
				group = 'Bedroom_4_Temps' 
			else:
				group = 'Bedroom_1_Temps'
		elif extinguish_event_idx == 1:
			group = 'Bedroom_1_Temps'
		else:
			group = 'Bedroom_2_Temps'

		# Get list of channel names
		channel_names = all_channels[all_channels['Primary_Chart']==group].index.values

		for name in channel_names:
			if 'TC7' in name:
				TC_7ft_name = name
				break

		# Make df of sensor group data to plot
		group_data = Exp_Data[channel_names].loc[start_df_idx-6:end_df_idx]

		# Calculate temp increase / time
		TC_7ft_min = [np.min(group_data[TC_7ft_name].loc[:start_df_idx+16]), 
						group_data[TC_7ft_name].loc[:start_df_idx+16].idxmin()]

		TC_7ft_max = [np.max(group_data[TC_7ft_name].loc[end_df_idx-15:]), 
				group_data[TC_7ft_name].loc[end_df_idx-15:].idxmax()]

		delta_T = TC_7ft_max[0]-TC_7ft_min[0]
		delta_t = TC_7ft_max[1]-TC_7ft_min[1]
		
		# Print 'Plotting [group] for [Test_Name]'
		print ('Plotting '+group.replace('_',' ')+' for '+Test_Name)

		print('  TC_7ft increase: '+str(delta_T)+' deg C')
		print('  Duration of increase: '+str(delta_t)+' sec')
		print('  Rate of increase: '+str(round(delta_T/delta_t,1))+' deg C/sec')

		# Create figure to for data plot
		fig = plt.figure()

		# Set plot colors/markers (ignore first 2 colors -- blue shade used on flow plots)
		mpl.rcParams['axes.prop_cycle'] = cycler(color=tableau20[2:])
		plot_markers = cycle(markers)

		# Set marker freq according to data sampling rate
		if Exp_Num=='18':
			mark_freq = 5
		else:
			mark_freq = 10

		# Set up primary x & y axes
		ax1 = plt.gca()
		ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
		ax1_xlims = ax1.axis()[0:2]
		plt.ylim([0, 1800])
		plt.yticks(fontsize=44)
		plt.xticks(fontsize=44)
		plt.xlabel('Time (sec)', fontsize=48)
		ax1.set_ylabel('Temperature ($^\circ$F)', fontsize=48)
		plt.grid(True)

		# Shade blue areas on plot for periods during which flow occurs
		plt.fill_between(flow_data.index.values, 0, 1800, where=flow_data['GPM']>10, facecolor='blue', alpha=0.3)

		# Plot flow data on secondary axis & set axis parameters
		ax2 = ax1.twinx()
		plt.plot(flow_data.index.values, flow_data['Total Gallons'], lw=6, color='#1f77b4')
		ax2.set_ylim(0,200)
		ax2.set_ylabel('Total Flow (Gallons)', fontsize=48)
		ax2.tick_params(labelsize=44)

		# Iterate through sensor group channels
		for channel in channel_names:
			# Skip plot quantity if channel name is blank, TC not desired, or 
			# 	channel listed under 'Excluded Channels' in description file
			if pd.isnull(channel):
				continue
			elif channel in channels_to_skip[File_Name]:
				continue
			elif int(channel[-1]) in skip_TCs:	# only plot TC 7, 5, 3, & 1
				continue		
			
			# Plot channel data on primary y axis
			ax1.plot(group_data[channel].index.values-start_df_idx, group_data[channel], lw=4,
				marker=next(plot_markers), markevery=int(mark_freq),
				mew=3, mec='none', ms=20, label=all_channels['Title'][channel])

		plt.xlim([-6,end_df_idx-start_df_idx])

		ax1.set_zorder(ax2.get_zorder()+1) # put temp data in front of flow data 
		ax1.patch.set_visible(False) # hide 'canvas' of ax1 so flow plot is visible 

		# Set up secondary x-axis & add event lines/labels
		ax3=ax1.twiny()
		ax3.set_zorder(ax1.get_zorder()) # put lines in front of all data
		ax3.set_xlim([-6,end_df_idx-start_df_idx])
		[ax3.axvline(time,color='0',lw=4) for time in event_times]
		ax3.set_xticks(event_times)
		plt.setp(plt.xticks()[1], rotation=60)
		ax3.set_xticklabels(event_labels, fontsize=30, ha='left')

		fig.set_size_inches(20, 18)
		
		# Set primary y axis range
		ax1.set_ylim(100,1800)

		# Add legend to figure
		handles1, labels1 = ax1.get_legend_handles_labels()
		plt.legend(handles1, labels1, loc='upper right', fontsize=40, handlelength=3, labelspacing=.15)

		plt.tight_layout()
		
		# Save figure to corresponding directory 
		plt.savefig(output_location+Test_Name+'_'+group+'.pdf')
		plt.close('all')
		print()

	set_idx = set_idx+1
   