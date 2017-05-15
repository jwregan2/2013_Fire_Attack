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

# Set file locations
data_location = '../0_Data/Ent_Experiment_Data/CSV/'
event_location = '../1_Info/Ent/Events/'
chart_location = '../2_Plots/Ent_Experiment_Plots/Bar_Graphs/'

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
	bar_group_values = np.empty([nrows,ncols])

	add_value = True

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

					# make list of BDP channels
					if Exp_Num == '3':	# Bad BDP for Experiment 3 
						BDP_channels = ['BDP41V','BDP42V','BDP43V','BDP45V']
					else:
						BDP_channels = ['BDP41V','BDP42V','BDP43V','BDP44V','BDP45V']

					Exp_Data_event = Exp_Data.loc[start_time:end_time, BDP_channels]

					for channel in BDP_channels:
						#Calculate velocity
						conv_inch_h2o = 0.04
						conv_pascal = 248.84
						convert_ftpm = 196.85
						end_zero_time = 45
						zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
						pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel]-zero_voltage)  # Convert voltage to pascals
						# Calculate flowrate
						Exp_Data_event[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (25+273.13)) * np.sign(pressure)
					
					# Add cfm to list of data
					CFM_ls.append(area*np.mean(Exp_Data_event[BDP_channels],axis=1))
					print(np.mean(area*np.mean(Exp_Data_event[BDP_channels],axis=1)))

				bar_group_values[i,j] = np.mean(CFM_ls)
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

					# make list of BDP channels
					BDP_channels = ['BDP41V','BDP42V','BDP43V','BDP44V','BDP45V']

					Exp_Data_event = Exp_Data.loc[start_time:end_time, BDP_channels]

					for channel in BDP_channels:
						#Calculate velocity
						conv_inch_h2o = 0.04
						conv_pascal = 248.84
						convert_ftpm = 196.85
						end_zero_time = 45
						zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
						pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel]-zero_voltage)  # Convert voltage to pascals
						# Calculate flowrate
						Exp_Data_event[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (25+273.13)) * np.sign(pressure)
					
					# Add cfm to list of data
					CFM_ls.append(area*np.mean(Exp_Data_event[BDP_channels],axis=1))
					print(np.mean(area*np.mean(Exp_Data_event[BDP_channels],axis=1)))

				bar_group_values[i,j] = np.mean(CFM_ls)
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

	fig, ax = plt.subplots(figsize=(10, 9))
	x_pos = list(range(len(event_group_labels)))
	width=0.85*(1./ncols)
	column_ID = 0
	for stream in stream_ls:
		if pattern_ls[0] != 'None':
			bar_label = stream+' '+pattern_ls[column_ID]
		else:
			bar_label = stream
		stream_pattern_values = bar_group_values[:,column_ID].tolist()
		if row['Change Sign']:
			stream_pattern_values = [value*-1. for value in stream_pattern_values]
		stream_pattern_variance = [value*0.18 for value in stream_pattern_values]
		plt.bar([x+width*column_ID for x in x_pos], stream_pattern_values, width,
			yerr=stream_pattern_variance, 
			color=tableau20[column_ID], label=bar_label, 
			error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
		column_ID = column_ID+1
	plt.ylabel('Average CFM (ft$^3$/min)', fontsize=18)
	plt.xticks([x+(ncols-1)*0.5*width for x in x_pos], event_group_labels, rotation = -15)
	ax.tick_params(axis='both', which='major', labelsize=16)
	plt.legend(loc=leg_loc,fontsize=11)
	savefig(chart_location+fig_name)
	print('Saved '+fig_name)
	print()
