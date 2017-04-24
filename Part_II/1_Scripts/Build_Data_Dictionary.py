# ******************************* Run Notes ********************************
# Creates the .dict files for the as a pickle object to be read for analysis

import pandas as pd
import os
import datetime as datetime
import numpy as np
from scipy.signal import butter, filtfilt
import pickle

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

data_location = '../2_Data/'
events_location = '../3_Info/Events/'

channel_list = pd.read_csv('../3_Info/Channels.csv').set_index('Channel')
channels_grouped = channel_list.groupby('Primary_Chart')

vent_info = pd.read_csv('../3_Info/Vent_Info.csv')
FED_info = pd.read_csv('../3_Info/FED_Info.csv')

transport_times = pd.read_csv('../3_Info/Updated_Transport_Times.csv').set_index('Experiment') 

exp_des = pd.read_csv('../3_Info/Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

for exp in exp_des.index.values:
	channels_to_skip[exp] = exp_des['Excluded Channels'][exp].split('|')

channels_to_trim = {}

#Generate pandas dataframe for each experiment with a list of channels to trim and what time. Index for dataframe is channel name. 
for exp in exp_des.index.values:
	if exp_des['Trimmed_Channels'][exp] == 'None':
		continue
	
	channels_to_trim[exp] = exp_des['Trimmed_Channels'][exp].split('|')
	
	chans, times = zip(*[val.split('_') for val in channels_to_trim[exp]])
	times = [int(t) for t in times]

	channels_to_trim[exp] = pd.DataFrame({'Channel':chans, 'Time':times}).set_index('Channel')
	

#Read in all experiment events to dictionary 'all_exp_events' with dataframe value = 'Experiment_X_Event' save to pickle file all_exp_events.p
print ('Reading in Experiment Events \n')
all_exp_events = {}

for exp in exp_des.index.values:
	exp = exp[:-4] + 'Events'
	all_exp_events[exp] = pd.read_csv(events_location + exp + '.csv').set_index('Event')

	events = [int((t - pd.to_datetime(all_exp_events[exp]['Time']['Ignition'])).total_seconds()) for t in pd.to_datetime(all_exp_events[exp]['Time']).tolist()]

	for e in np.arange(0,len(events)):
		if events[e] % 2 != 0:
			events[e] = events [e] + 1

	all_exp_events[exp]['Time_Seconds'] = events

	print (exp + ' Read')

pickle.dump(all_exp_events, open (events_location + 'all_exp_events.dict' , 'wb'))

print ('\n')
print ('-------------- all_exp_events.dict dumped to data folder ------------------')


#Read in all experiment data to dictionary 'all_exp_data' with the dataframe value = 'Experiment_X_Data' save to pickle file all_exp_data.p
print ('\n')
print ('Reading in Experiment Data \n')

all_exp_data = {}

for exp in exp_des.index.values:

	data = pd.read_csv(data_location +  exp + '.csv')
	
	all_exp_data[exp] = pd.DataFrame()

	#Adjust time to lowest common sample rate (2 seoncds) and truncate date to be from 0 to end experiment
	if exp_des['Speed'][exp] == 'high':
		data = data[::20]
		time = [datetime.datetime.strptime(t, '%H:%M:%S.%f') for t in data['Elapsed Time']]

	if exp_des['Speed'][exp] == 'low':
		if exp_des['House'][exp] == 'a':
			data= data[::2]
			time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in data['Elapsed Time']]
		if exp_des['House'][exp] == 'b':
			time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in data['Elapsed Time']]

	# print (all_exp_events[exp[:-4]+'Events']['Time'][1])
	ignition = datetime.datetime.strptime(all_exp_events[exp[:-4]+'Events']['Time'][0], '%H:%M:%S')

	#Adjust time to be every 2 seconds regardless of the drift. 
	time = [int((t - ignition).total_seconds()) for t in time]

	if time[0] % 2 != 0:
		time[0] = time[0]+1

	if time[-1] % 2 != 0:
		time[-1] = time[-1]+1
	
	new_time = np.arange(time[0], time[-1], 2)

	if len(new_time) < len(data.index):		
		add_time = np.arange(new_time[-1]+2, new_time[-1]+(len(data.index)-len(new_time)+2)*2,2)
		new_time = np.append(new_time, add_time)

	data['Time'] = new_time[:len(data.index)]
	data.set_index('Time', inplace = True)

	data = data.ix[0:all_exp_events[exp[:-4]+'Events']['Time_Seconds']['End Experiment']]

	all_exp_data[exp] = data

	for channel in channel_list.index.values:

		#Skip channels listed in experiment discription file
		if channel in channels_to_skip[exp]: 
			continue

		if channel not in all_exp_data[exp]:
			continue

		# If statement to find temperature type in channels csv
		if channel_list['Type'][channel] == 'Temperature':
			
			# Set data to include slope and intercept
			all_exp_data[exp][channel] = all_exp_data[exp][channel] * channel_list['ScaleFactor_' + exp_des['House'][exp].upper()][channel] + channel_list['Offset'][channel]
			all_exp_data[exp][channel] = all_exp_data[exp][channel].round(1)
		
		#If statement to find gas or carbon monoxide type in channels csv
		if channel_list['Type'][channel] in ['Gas', 'Carbon Monoxide']:
			
			all_exp_data[exp][channel] = all_exp_data[exp][channel] * channel_list['ScaleFactor_' + exp_des['House'][exp].upper()][channel]  + channel_list['Offset'][channel]

			#Update Data based on transport time
			transport = int(transport_times['Victim_' + channel[0] + '_' + exp_des['House'][exp].upper()][exp])	

			if transport % 2 != 0:
				transport = transport - 1

			all_exp_data[exp][channel] = pd.DataFrame({'Time':all_exp_data[exp].index.values[:-int(transport/2)], 'channel':all_exp_data[exp][channel][int(transport/2):]}).set_index('Time')

			#Normalize Oxygen to 20.95 and round to 2
			if channel[1:] == 'O2V':
				all_exp_data[exp][channel] = (all_exp_data[exp][channel] - all_exp_data[exp][channel][:90].mean()) + 20.95
				all_exp_data[exp][channel] = all_exp_data[exp][channel].round(2)

			if channel[1:] == 'CO2V':
				all_exp_data[exp][channel] = all_exp_data[exp][channel].round(2)

			if channel[1:] == 'COV':
				all_exp_data[exp][channel] = all_exp_data[exp][channel].round(0)

		if channel_list['Type'][channel] in ['Heat Flux', 'Victim Heat Flux']:
			all_exp_data[exp][channel] = all_exp_data[exp][channel] * channel_list['ScaleFactor_' + exp_des['House'][exp].upper()][channel]  + channel_list['Offset'][channel]
			all_exp_data[exp][channel] = all_exp_data[exp][channel].round(2)

        # If statement to find velocity type in channels csv
		if channel_list['Type'][channel] == 'Velocity':

			# Define cutoff and fs for filtering 
			cutoff = 50
			fs = 700
			all_exp_data[exp][channel] = all_exp_data[exp][channel] - np.average(all_exp_data[exp][channel][:90]) + 2.5
			all_exp_data[exp][channel] = butter_lowpass_filtfilt(all_exp_data[exp][channel], cutoff, fs)
			
			#Calculate new index for velocity result
			all_exp_data[exp][channel[:-1]] = (np.sign(all_exp_data[exp][channel]-2.5)*0.070*((all_exp_data[exp][channel[:-1]+'T']+273.15)*(99.6*abs(all_exp_data[exp][channel]-2.5)))**0.5) * 2.23694
			all_exp_data[exp][channel[:-1]] = all_exp_data[exp][channel[:-1]].round(2)

		if exp in channels_to_trim:
			if channel in channels_to_trim[exp].index:
				if channel_list['Type'][channel] == 'Velocity':
					all_exp_data[exp][channel[:-1]] = all_exp_data[exp].ix[channel[:-1]][:ind(channels_to_trim[exp]['Time'][channel])]
				else:
					all_exp_data[exp][channel] = all_exp_data[exp][channel][:int(channels_to_trim[exp]['Time'][channel]/2)]

	print (exp + ' Read')

pickle.dump(all_exp_data, open (data_location + 'all_exp_data.dict' , 'wb'))

print ('\n')
print ('-------------- all_exp_data.dict dumped to data folder ------------------')

