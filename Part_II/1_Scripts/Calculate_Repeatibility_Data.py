#******************************** Run notes *******************************
# Must be run affter Build_Data_Dictionary.py to build pickle file of data.
# Calculates the average temperature at each tree over the 30 seconds prior to the first event
# And saves the data as a .csv file in the ../2_Data/Repeatibility_Data/ folder
# Uses vent_info.csv to determine the ventilation profile each experiment. 


import pandas as pd
import os
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt
import pickle

data_location = '../2_Data/'
events_location = '../3_Info/Events/'

channel_list = pd.read_csv('../3_Info/Channels.csv').set_index('Channel')
channels_grouped = channel_list.groupby('Primary_Chart')

vent_info = pd.read_csv('../3_Info/Vent_Info.csv')

exp_des = pd.read_csv('../3_Info/Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

for exp in exp_des.index.values:
	channels_to_skip[exp] = exp_des['Excluded Channels'][exp].split('|')

#Read in pickle file for data
all_exp_data = pickle.load( open( data_location + 'all_exp_data.dict', 'rb' ) )
all_exp_events = pickle.load( open (events_location + 'all_exp_events.dict', 'rb'))


# -------------------------------Calculate and output Repeatibility Data-------------------------------
running_comp = {}

output_location = '../2_Data/Repeatibility_Data'

for vent in vent_info.columns:

	for exp in vent_info[vent].dropna():

		if vent not in running_comp:
			running_comp[vent] = {}

		if exp not in running_comp[vent]:
			running_comp[vent][exp] = pd.DataFrame()

		first_event = all_exp_events[exp[:-4] + 'Events']['Time_Seconds'].ix[1]

		running_comp[vent][exp] = all_exp_data[exp].ix[first_event-30:first_event]	

repeatability_data  = {}

if not os.path.exists(output_location):
	os.makedirs(output_location)

for vent in vent_info.columns.values:

	if vent not in repeatability_data:
		repeatability_data[vent] = {}

	for exp in vent_info[vent].dropna():
		print (exp)

		for channel_group in channels_grouped.groups:

			if channel_list['Type'][channels_grouped.get_group(channel_group).index.values[0]] != 'Temperature':
				continue

			if 'Skin' in channel_group:
				continue

			group_values = pd.DataFrame()


			for channel in channels_grouped.get_group(channel_group).index.values:

				if channel not in running_comp[vent][exp].keys():
					continue 

				if channel in channels_to_skip:
					continue

				value = pd.DataFrame(running_comp[vent][exp][channel])

				group_values = pd.concat([group_values, value], axis =1)

			group_values = group_values.mean(axis=1)

			if exp not in repeatability_data[vent]:
				repeatability_data[vent][exp] = {}

			repeatability_data[vent][exp][channel_group]=group_values.mean()

	repeatability_data_csv = pd.DataFrame.from_dict(repeatability_data[vent])
	repeatability_data_csv = repeatability_data_csv.reset_index()
	repeatability_data_csv.rename(columns={'index':'Location'}, inplace=True)

	data_types = []
	for location in repeatability_data_csv['Location']:
		if 'Temps' in location:
			data_types = data_types + ['Temperature']
		elif 'HF' in location:
			data_types = data_types + ['Heat Flux']
		elif 'Carbon' in location:
			data_types = data_types + ['Carbon Monoxide']
		elif 'CO2' in location:
			data_types = data_types + ['Carbon Dioxide']
		elif 'O2' in location:
			data_types = data_types + ['Oxygen']

	repeatability_data_csv['Type'] = data_types

	repeatability_data_csv.to_csv(output_location + '/' + vent + '.csv', index=False)

	print ('------------------' + vent + '.csv saved in ' + output_location + '------------------')
