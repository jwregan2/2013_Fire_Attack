import pandas as pd
import os
import datetime as datetime
import numpy as np

data_location = '../2_Data/'
events_location = '../3_Info/Events/'

channel_list = pd.read_csv('../3_Info/Channels.csv')
channel_list = channel_list.set_index('Channel')

vent_info = pd.read_csv('../3_Info/Vent_Info.csv')

exp_des = pd.read_csv('../3_Info/Description_of_Experiments.csv')
exp_des = exp_des.set_index('Experiment')

#Read in all experiment events to dictionary 'all_exp_events' with dataframe value = 'Experiment_X_Event'
print ('Reading in Experiment Events \n')
all_exp_events = {}

for exp in exp_des.index.values:
	exp = exp[:-4] + 'Events'
	events = pd.read_csv(events_location + exp + '.csv')
	all_exp_events[exp] = events.set_index('Event')

#Read in all experiment data to dictionary 'all_exp_data' with the dataframe value = 'Experiment_X_Data'
print ('Reading in Experiment Data \n')
all_exp_data = {}

for exp in exp_des.index.values:
	data = pd.read_csv(data_location +  exp + '.csv')
	all_exp_data[exp] = data.set_index('Elapsed Time')

	if exp_des['Speed'][exp] == 'high':
		time = [datetime.datetime.strptime(t, '%H:%M:%S.%f') for t in all_exp_data[exp].index]
	if exp_des['Speed'][exp] == 'low':
		time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in all_exp_data[exp].index]

	event = datetime.datetime.strptime(all_exp_events[exp[:-4]+'Events']['Time'][1], '%H:%M:%S')

	time = [ (t-event).total_seconds() for t in time]

	all_exp_data[exp].index = time

# Comprare fire room temps no_vent

# channels = ['1TC1','1TC3','1TC5','1TC7']

running_comp = {}

for channel in channel_list.index:

	for vent in vent_info.columns:

		comp_data = pd.DataFrame({'Time':np.arange(-30,-5,2)})
		comp_data = comp_data.set_index('Time')


		for exp in vent_info[vent].dropna():

			if channel not in all_exp_data[exp]:
				continue

			data = all_exp_data[exp][channel]

			if exp_des['Speed'][exp] == 'high':
					data = data[-30:-5:20]

			if exp_des['Speed'][exp] == 'low':
				if exp_des['House'][exp] == 'a':
					data = data[-30:-5:2]
				if exp_des['House'][exp] == 'b':
					data = data[-30:-5]

			data.name = exp

			data = data.reset_index(drop=True)
			

			if len(data) != 13:
				data = data[0:13]

			data.index = np.arange(-30,-5,2)

			comp_data = pd.concat([comp_data,data], axis=1, join='inner')
		
		comp_data = comp_data.mean()
		comp_data.name = channel

		if vent not in running_comp:
			running_comp[vent] = comp_data
		else:
			running_comp[vent] = pd.concat([running_comp[vent], comp_data], axis=1)

	# for vent in vent_info.columns:
	# 	print (running_comp[vent].mean())
	# 	# running_comp[vent].append(running_comp[vent].mean()) 

print (running_comp['Single_Vent'].mean())
# print (running_comp['Single_Vent'])

	# print (running_comp['No_Vent'] > running_comp['No_Vent'] + running_comp['No_Vent'].std())
	# print (running_comp['No_Vent'] < running_comp['No_Vent'] - running_comp['No_Vent'].std())
