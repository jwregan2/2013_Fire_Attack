#####################################################################################
# Script generates CFM and pressure bar graphs based on sensores at start of hallway 
# 	for entrainment experiments specified in the file bar_graph_list.csv located 
#	in the info directory
#####################################################################################

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

# Set file locations
data_location = '../0_Data/Ent_Experiment_Data/CSV/'
event_location = '../1_Info/Ent/Events/'
CFM_graph_dir = '../2_Plots/Ent_Experiment_Plots/CFM_Bar_Graphs/'
Pressure_graph_dir = '../2_Plots/Ent_Experiment_Plots/Pressure_Bar_Graphs/'

# Read in channel list
channel_list = pd.read_csv('../1_Info/Ent/Channels_List.csv')
# Set index value for channels as 'Channel'
channel_list = channel_list.set_index('Channel')

# Read in description of experiments; set index of description of experiments
info_file = '../1_Info/Ent/bar_graph_list.csv'
info_df = pd.read_csv(info_file)

area = 17.778

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

for index, row in info_df.iterrows():
	fig_name = row['Fig_Name']
	bar_groups = row['Bar_Groups'].split('|')
	if row['Event_Group_Ref'] == 'Same': 	# make list for different bar groups
		event_group_labels = bar_groups
	else:
		event_group_labels = row['Event_Group_Ref'].split('|')
	stream_ls = row['Stream'].split('|')	# list of different streams per group
	pattern_ls = row['Pattern'].split('|')	# list of different patterns per group
	event_order = row['Event_Label_Order'].split('|')	# order of words in event description
	experiment_files = row['Experiments'].split('|')	# experiments to obtain avgs from 

	# empty array to add avg values to
	ncols = len(stream_ls)
	nrows = len(event_group_labels)
	CFM_bar_group_values = np.empty([nrows,ncols])
	Pressure_bar_group_values = np.empty([nrows,ncols])

	if row['Same_Events']:		# identical experiment files
		i = 0
		for group in event_group_labels:
			j = 0
			for stream in stream_ls:
				pattern = pattern_ls[j] # get pattern for specific stream 
				event_IDs = []
				for part in event_order:	# make string corresponding to specific event
					if part == 'Stream':
						event_IDs.append(stream)
					elif part == 'Group':
						event_IDs.append(group)
					elif part == 'Pattern':
						event_IDs.append(pattern)
					else:
						print('[ERROR]: INVALID ENTRY IN event_order')
						sys.exit()

				CFM_ls = []
				Pressure_ls = []
				for Test_Name in experiment_files: 	# loop through each experiment
					# Get exp number; read in event file
					Exp_Num = Test_Name[11:]
					Exp_Events = pd.read_csv(event_location+Test_Name+'_Events.csv')

					# Get event index and from that start + end times for event
					event_label = event_IDs[0]+' '+event_IDs[1]+' '+event_IDs[2]
					print(Test_Name+' '+event_label)

					event_index = Exp_Events[Exp_Events['Event']==event_label].index.tolist()[0]
					
					h, mm, ss = Exp_Events['Elapsed_Time'][event_index].split(':')
					start_time = 3600*int(h)+60*int(mm)+int(ss)
					h, mm, ss = Exp_Events['Elapsed_Time'][event_index+1].split(':')
					end_time = 3600*int(h)+60*int(mm)+int(ss)

					Exp_Data = pd.read_csv(data_location+Test_Name+'_Data.csv')

					# Make list of BDP & Pressure channels
					if Exp_Num == '3':	# Bad BDPs for Experiment 3 
						BDP_channels = ['BDP42V','BDP43V','BDP45V']
					else:
						BDP_channels = ['BDP41V','BDP42V','BDP43V','BDP44V','BDP45V']
					Pressure_channels = ['PT21V','PT24V','PT27V']

					Exp_Data_event = Exp_Data.loc[start_time:end_time, BDP_channels+Pressure_channels]

					# Define conversion constants
					conv_inch_h2o = 0.04
					conv_pascal = 248.84
					convert_ftpm = 196.85
					end_zero_time = 45

					# Calculate velocity
					for channel in BDP_channels:
						zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
						pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel]-zero_voltage)  # Convert voltage to pascals
						# Calculate flowrate
						if int(Exp_Num) > 4:
							Exp_Data_event[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (Exp_Data[channel[:-1]+'T']+273.15)) * np.sign(pressure)
						else:
							Exp_Data_event[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * 289.) * np.sign(pressure)

					# Calculate pressure
					for channel in Pressure_channels:
						channel_data = Exp_Data_event[channel]

						# Read scale factor and offset for channel and determine zero value 
						scale_factor = channel_list['ScaleFactor'][channel]
						offset = channel_list['Offset'][channel]
						zero_value = np.mean(Exp_Data[channel][0:end_zero_time]*scale_factor+offset)
						
						# Convert data to pressure 
						channel_data = scale_factor * channel_data + offset 
						channel_data = channel_data-zero_value

						# Update dataframe with converted data
						Exp_Data_event[channel] = channel_data

					# Add cfm and pressures to list of data
					CFM_ls.append(area*np.mean(Exp_Data_event[BDP_channels]))
					Pressure_ls.append(np.mean(Exp_Data_event[Pressure_channels]))
					print(np.mean(area*np.mean(Exp_Data_event[BDP_channels])))
					print(np.mean(np.mean(Exp_Data_event[Pressure_channels])))
					
				CFM_bar_group_values[i,j] = np.mean(CFM_ls)
				Pressure_bar_group_values[i,j] = np.mean(Pressure_ls)*0.000145038	
				j = j+1
			
			i = i+1

	else:
		i = 0
		for group in event_group_labels:
			j = 0
			for stream in stream_ls:
				if pattern_ls[0] != 'None':
					pattern = pattern_ls[j] # get pattern for specific stream 
				else:
					pattern = pattern_ls[0]

				event_IDs = []
				for part in event_order:	# make string corresponding to specific event
					if part == 'Stream':
						event_IDs.append(stream)
					elif part == 'Group':
						event_IDs.append(group)
					elif part == 'Pattern':
						event_IDs.append(pattern)
					else:
						print('[ERROR]: INVALID ENTRY IN event_order')
						sys.exit()

				if index == 8 and i > 2:
					Test_Names = experiment_files[-1]
				else:
					Test_Names = experiment_files[j]

				CFM_ls = []
				Pressure_ls = []

				for Test_Name in Test_Names.split(','):
					# Get exp number; read in event file
					Exp_Num = Test_Name[11:]
					Exp_Events = pd.read_csv(event_location+Test_Name+'_Events.csv')

					if len(event_IDs) < 3:
						event_label = event_IDs[0]+' '+event_IDs[1]
					else:
						event_label = event_IDs[0]+' '+event_IDs[1]+' '+event_IDs[2]
					
					print(Test_Name+' '+event_label)

					event_index = Exp_Events[Exp_Events['Event']==event_label].index.tolist()[0]

					h, mm, ss = Exp_Events['Elapsed_Time'][event_index].split(':')
					start_time = 3600*int(h)+60*int(mm)+int(ss)
					h, mm, ss = Exp_Events['Elapsed_Time'][event_index+1].split(':')
					end_time = 3600*int(h)+60*int(mm)+int(ss)

					Exp_Data = pd.read_csv(data_location+Test_Name+'_Data.csv')

					# make list of BDP & Pressure channels
					BDP_channels = ['BDP41V','BDP42V','BDP43V','BDP44V','BDP45V']
					Pressure_channels = ['PT21V','PT24V','PT27V']

					Exp_Data_event = Exp_Data.loc[start_time:end_time, :]

					# Define conversion constants
					conv_inch_h2o = 0.04
					conv_pascal = 248.84
					convert_ftpm = 196.85
					end_zero_time = 45

					# Calculate velocity
					for channel in BDP_channels:
						zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
						pressure = conv_inch_h2o * conv_pascal * (Exp_Data_event[channel]-zero_voltage)  # Convert voltage to pascals
						# Calculate flowrate
						if int(Exp_Num) > 4:
							Exp_Data_event[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (Exp_Data_event[channel[:-1]+'T']+273.13)) * np.sign(pressure)
						else:
							Exp_Data_event[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * 289.) * np.sign(pressure)

					# Calculate pressure
					for channel in Pressure_channels:
						channel_data = Exp_Data_event[channel]

						# Read scale factor and offset for channel and determine zero value 
						scale_factor = channel_list['ScaleFactor'][channel]
						offset = channel_list['Offset'][channel]
						zero_value = np.mean(Exp_Data[channel][0:end_zero_time]*scale_factor+offset)
						
						# Convert data to pressure 
						channel_data = scale_factor * channel_data + offset 
						channel_data = channel_data-zero_value

						# Update dataframe with converted data
						Exp_Data_event[channel] = channel_data

					# Add cfm and pressures to list of data
					CFM_ls.append(area*np.mean(Exp_Data_event[BDP_channels]))
					Pressure_ls.append(np.mean(Exp_Data_event[Pressure_channels]))
					print(np.mean(area*np.mean(Exp_Data_event[BDP_channels])))
					print(np.mean(np.mean(Exp_Data_event[Pressure_channels])))

				CFM_bar_group_values[i,j] = np.mean(CFM_ls)
				Pressure_bar_group_values[i,j] = np.mean(Pressure_ls)*0.000145038
				j = j+1

			i = i+1
	
	print()
	# Fix specific group label
	if event_group_labels[0] == 'Room':
		event_group_labels[0] = 'Room Sweep'

	if index == 0:
		leg_loc = 'upper right'
	elif index == 1:
		leg_loc = 'lower right'
	else:
		leg_loc = 'upper left'

	# Generate CFM bar graph
	fig, ax = plt.subplots(figsize=(10, 9))
	x_pos = list(range(len(event_group_labels)))

	# Check if 4 or more bars are to be plotted & adjust width accordingly
	# 	(Note: ncols = number of bars per group, nrows = number of groups)
	if ncols*nrows >= 4:
		width=0.85*(1./ncols)
		filler_bars = False
	else:
		filler_bars = True 	# make psuedo bars to keep width reasonable	
		width=0.65*(1./ncols)
	
	column_ID = 0
	for stream in stream_ls:
		# Set legend label for given bar
		if pattern_ls[0] != 'None':
			bar_label = stream+' '+pattern_ls[column_ID]
		else:
			bar_label = stream

		# Make list of each group of bars & and make all values positive, if desired
		stream_pattern_values = CFM_bar_group_values[:,column_ID].tolist()
		if row['Change Sign']:
			stream_pattern_values = [value*-1. for value in stream_pattern_values]

		# Make list of error bar variances
		stream_pattern_variance = [value*0.18 for value in stream_pattern_values]

		# Plot bars for specific stream/pattern combo & move to next set of bars
		if filler_bars: # leave space for filler bars
			if len(x_pos) == 1:
				plt.bar([x+width*(column_ID+1) for x in x_pos], stream_pattern_values, width=width,
					yerr=stream_pattern_variance, 
					color=tableau20[column_ID], label=bar_label, 
					error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
			else:
				plt.bar([x*0.75+width*(x+1) for x in x_pos], stream_pattern_values, width=width,
					yerr=stream_pattern_variance, 
					color=tableau20[column_ID], label=bar_label, 
					error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
		else:
			plt.bar([x+width*column_ID for x in x_pos], stream_pattern_values, width=width,
				yerr=stream_pattern_variance, 
				color=tableau20[column_ID], label=bar_label, 
				error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
		column_ID = column_ID+1

	# Add filler bars (if applicable) & set x-axis ticks/labels
	if filler_bars:
		if len(x_pos) == 1:
			plt.bar([x_pos[0],x_pos[0]+(ncols+1)*width], [0,0], width=width)
			tick_offset = 1.5*width
		else:
			plt.bar([1.25*x+tick_offset*(x+1) for x in x_pos], [0,0], width=width, color='red')
			tick_offset = width
		plt.xticks([0.75*x+tick_offset*(x+1) for x in x_pos], event_group_labels, rotation = -15)
		ax.tick_params(axis='both', which='major', labelsize=16)
	else:
		plt.xticks([x+(ncols-1)*0.5*width for x in x_pos], event_group_labels, rotation = -15)
		ax.tick_params(axis='both', which='major', labelsize=16)
	
	# Set y-axis label and legend & save figure
	plt.ylabel('Average CFM (ft$^3$/min)', fontsize=18)
	plt.legend(loc=leg_loc,fontsize=11)
	savefig(CFM_graph_dir+fig_name)
	print('Saved '+fig_name+' (CFM)')

	# Generate pressure bar graphs
	fig, ax = plt.subplots(figsize=(10, 9))
	x_pos = list(range(len(event_group_labels)))

	# Check if 4 or more bars are to be plotted & adjust width accordingly
	# 	(Note: ncols = number of bars per group, nrows = number of groups)
	if ncols*nrows >= 4:
		width=0.85*(1./ncols)
		filler_bars = False
	else:
		filler_bars = True 	# make psuedo bars to keep width reasonable	
		width=0.65*(1./ncols)
	
	column_ID = 0
	for stream in stream_ls:
		# Set legend label for given bar
		if pattern_ls[0] != 'None':
			bar_label = stream+' '+pattern_ls[column_ID]
		else:
			bar_label = stream

		# Make list of each group of bars & and make all values positive, if desired
		stream_pattern_values = Pressure_bar_group_values[:,column_ID].tolist()
		if row['Change Sign']:
			stream_pattern_values = [value*-1. for value in stream_pattern_values]

		# Make list of error bar variances
		stream_pattern_variance = [value*0.18 for value in stream_pattern_values]

		# Plot bars for specific stream/pattern combo & move to next set of bars
		if filler_bars: # leave space for filler bars
			if len(x_pos) == 1:
				plt.bar([x+width*(column_ID+1) for x in x_pos], stream_pattern_values, width=width,
					yerr=stream_pattern_variance, 
					color=tableau20[column_ID], label=bar_label, 
					error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
			else:
				plt.bar([x*0.75+width*(x+1) for x in x_pos], stream_pattern_values, width=width,
					yerr=stream_pattern_variance, 
					color=tableau20[column_ID], label=bar_label, 
					error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
		else:
			plt.bar([x+width*column_ID for x in x_pos], stream_pattern_values, width=width,
				yerr=stream_pattern_variance, 
				color=tableau20[column_ID], label=bar_label, 
				error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
		column_ID = column_ID+1

	# Add filler bars (if applicable) & set x-axis ticks/labels
	if filler_bars:
		if len(x_pos) == 1:
			plt.bar([x_pos[0],x_pos[0]+(ncols+1)*width], [0,0], width=width)
			tick_offset = 1.5*width
		else:
			plt.bar([1.25*x+tick_offset*(x+1) for x in x_pos], [0,0], width=width, color='red')
			tick_offset = width
		plt.xticks([0.75*x+tick_offset*(x+1) for x in x_pos], event_group_labels, rotation = -15)
		ax.tick_params(axis='both', which='major', labelsize=16)
	else:
		plt.xticks([x+(ncols-1)*0.5*width for x in x_pos], event_group_labels, rotation = -15)
		ax.tick_params(axis='both', which='major', labelsize=16)
	
	# Set y-axis label and legend & save figure
	plt.ylabel('Average Pressure (psi)', fontsize=18)
	plt.legend(loc=leg_loc,fontsize=11)
	savefig(Pressure_graph_dir+fig_name)
	print('Saved '+fig_name+' (Pressure)')
	print()
