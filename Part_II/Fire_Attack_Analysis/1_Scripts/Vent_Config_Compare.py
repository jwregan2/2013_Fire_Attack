import pandas as pd
import os
import datetime as datetime
import numpy as np

data_location = '../2_Data/'
events_location = '../3_Info/Events/'

channel_list = pd.read_csv('../3_Info/Channels.csv')
channel_list = channel_list.set_index('Channel')

channel_list = channel_list.groupby('Primary_Chart')

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

experiments = ['Experiment_1_Data', 'Experiment_2_Data']

for exp in exp_des.index.values:
# for exp in experiments:
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

for vent in vent_info.columns:
	comp_data = pd.DataFrame({'Time':np.arange(-30,-5,2)})
	comp_data = comp_data.set_index('Time')

	for exp in vent_info[vent].dropna():

		# if exp not in experiments:
		# 	continue

		data = all_exp_data[exp]

			# fire_room_channels=['1TC1', '1TC3', '1TC5', '1TC7']
			
			# fire_room_temps = pd.DataFrame({'1TC1':all_exp_data['Experiment_2_Data']['1TC1'], '1TC3':all_exp_data['Experiment_2_Data']['1TC3'], '1TC5':all_exp_data['Experiment_2_Data']['1TC5'], '1TC7':all_exp_data['Experiment_2_Data']['1TC7']})

			# print (fire_room_temps[0:10])
			# print (fire_room_temps.mean(axis=1)[0:10])
			# exit()

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

		if vent not in running_comp:
			running_comp[vent] = {}
			running_comp[vent][exp] = data
		else:
			running_comp[vent][exp] = data

No_Vent_Temps = {}

for exp in vent_info['No_Vent'].dropna():

	Bedroom_1_Temps = pd.DataFrame()

	for channel in channel_list.get_group('Bedroom_1_Temps').index.values:
		
		Temp = pd.DataFrame(running_comp['No_Vent'][exp][channel])
		Temp = Temp.mean()

		Bedroom_1_Temps = pd.concat([Bedroom_1_Temps, Temp])

	print(Bedroom_1_Temps)
	No_Vent_Temps[exp]=Bedroom_1_Temps.mean()

print(No_Vent_Temps)

