# ******************************* Run Notes ********************************
# Creates the .dict files for pickle to read as an object during analysis

import pandas as pd
import os
import datetime as datetime
import numpy as np
from scipy.signal import butter, filtfilt,savgol_filter
import pickle
import matplotlib.pyplot as plt


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

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

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
	

#Read in all experiment events to dictionary 'all_exp_events' with dataframe value = 'Experiment_X_Event' save to pickle file all_exp_events.dict
print ('Reading in Experiment Events \n')
all_exp_events = {}
ignition_date_time = {}

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

#Read in all experiment data to dictionary 'all_exp_data' with the dataframe value = 'Experiment_X_Data' save to pickle file all_exp_data.dict
print ('\n')
print ('Reading in Experiment Data \n')

all_exp_data = {}
all_exp_FED_data = {}

for exp in exp_des.index.values:

	data = pd.read_csv(data_location +  exp + '.csv')
	
	all_exp_data[exp] = pd.DataFrame()
	all_exp_FED_data[exp] = pd.DataFrame()
	
	#Adjust time to lowest common sample rate (2 seoncds) and truncate date to be from 0 to end experiment
	if exp_des['Speed'][exp] == 'high':
		time = [datetime.datetime.strptime(t, '%H:%M:%S.%f') for t in data['Elapsed Time']]

	if exp_des['Speed'][exp] == 'low':
		if exp_des['House'][exp] == 'a':
			time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in data['Elapsed Time']]
		if exp_des['House'][exp] == 'b':
			time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in data['Elapsed Time']]

	ignition = datetime.datetime.strptime(all_exp_events[exp[:-4]+'Events']['Time'][0], '%H:%M:%S')

	data['Time'] = [int((t - ignition).total_seconds()) for t in time]
	data.set_index('Time', inplace = True)

	data = data.ix[0:all_exp_events[exp[:-4]+'Events']['Time_Seconds']['End Experiment']]

	all_exp_data[exp] = data

	if exp_des['Speed'][exp] == 'high':
		new_exp_df = pd.DataFrame(np.arange(0,all_exp_data[exp].index.values[-1]+1,1), columns=['Time'])
		new_exp_df = new_exp_df.set_index('Time')

	# step = [j-i for i, j in zip(all_exp_data[exp].index.tolist()[:-1], all_exp_data[exp].index.tolist()[1:])]
	# plt.plot(step)
	# plt.show()
	# exit()

	for channel in channel_list.index.values:
		# Skip channels listed in experiment description file
		if channel in channels_to_skip[exp]: 
			continue

		if channel not in all_exp_data[exp]:
			continue

		# If statements to find data type of channel & process data accordingly
		# Temperature
		if channel_list['Type'][channel] == 'Temperature':
			# Set data to include slope and intercept
			all_exp_data[exp][channel] = all_exp_data[exp][channel] * channel_list['ScaleFactor_' + exp_des['House'][exp].upper()][channel] + channel_list['Offset'][channel]
			rounding_value = 1
		
		# Gas or carbon monoxide 
		elif channel_list['Type'][channel] in ['Gas', 'Carbon Monoxide']:
			# Set data to include slope and intercept & shift based on transport time
			all_exp_data[exp][channel] = all_exp_data[exp][channel] * channel_list['ScaleFactor_' + exp_des['House'][exp].upper()][channel]  + channel_list['Offset'][channel]
			transport = int(transport_times['Victim_' + channel[0] + '_' + exp_des['House'][exp].upper()][exp])	

			if transport % 2 != 0:
				transport = transport - 1

			if exp_des['Speed'][exp] == 'high':
				all_exp_data[exp][channel] = pd.DataFrame({'channel':all_exp_data[exp][channel][int(transport):].tolist()})
			
			elif exp_des['Speed'][exp] == 'low':
				if exp_des['House'][exp] == 'a':
					all_exp_data[exp][channel] = pd.DataFrame({'channel':all_exp_data[exp][channel][int(transport):].tolist()})
				elif exp_des['House'][exp] == 'b':
					all_exp_data[exp][channel] = pd.DataFrame({'channel':all_exp_data[exp][channel][int(transport/2):].tolist()})
			
			#Normalize Oxygen to 20.95 and round to 2
			if channel[1:] == 'O2V':
				all_exp_data[exp][channel] = (all_exp_data[exp][channel] - all_exp_data[exp][channel][:90].mean()) + 20.95
				rounding_value = 2

			elif channel[1:] == 'CO2V':
				rounding_value = 2

			elif channel[1:] == 'COV':
				rounding_value = 0

		# Heat flux
		elif channel_list['Type'][channel] in ['Wall Heat Flux', 'Floor Heat Flux', 'Victim Heat Flux']:
			# Set data to include slope and intercept
			all_exp_data[exp][channel] = all_exp_data[exp][channel] * channel_list['ScaleFactor_' + exp_des['House'][exp].upper()][channel]  + channel_list['Offset'][channel]
			rounding_value = 2

        # Velocity
		elif channel_list['Type'][channel] == 'Velocity':
			# Zero voltage
			all_exp_data[exp][channel] = all_exp_data[exp][channel] - np.average(all_exp_data[exp][channel][:90]) + 2.5

			# Convert voltage to velocity
			all_exp_data[exp][channel[:-1]] = (np.sign(all_exp_data[exp][channel]-2.5)*0.070*((all_exp_data[exp][channel[:-1]+'T']+273.15)*(99.6*abs(all_exp_data[exp][channel]-2.5)))**0.5) * 2.23694
			rounding_value = 2

			if exp_des['Speed'][exp] == 'high':
				all_exp_data[exp][channel[:-1]] = savgol_filter(all_exp_data[exp][channel[:-1]],75,3)
			elif exp_des['Speed'][exp] == 'low':
				all_exp_data[exp][channel[:-1]] = savgol_filter(all_exp_data[exp][channel[:-1]],11,3)

		all_exp_data[exp][channel] = all_exp_data[exp][channel].round(rounding_value)

		if exp in channels_to_trim:
			if channel in channels_to_trim[exp].index:
				if channel_list['Type'][channel] == 'Velocity':
					if channel[:-1] in all_exp_data[exp]:
						all_exp_data[exp][channel[:-1]] = all_exp_data[exp][channel[:-1]][:int(channels_to_trim[exp]['Time'][channel]/2)]
				else:
					all_exp_data[exp][channel] = all_exp_data[exp][channel][:int(channels_to_trim[exp]['Time'][channel]/2)]

		# Average data over each second & add to new df if sampling at high rate
		if exp_des['Speed'][exp] == 'high':
			new_channel_data = all_exp_data[exp][channel][9:].rolling(window=10, center=False).mean()
			new_channel_data = new_channel_data.dropna()
			new_channel_data = new_channel_data[::10]
			new_exp_df[channel] = new_channel_data.round(rounding_value)
			# for n in range(0,new_exp_df.index.values[-1]+1):
			# 	orig_avg = round(np.mean(all_exp_data[exp][channel].iloc[n*10+9:19+n*10]),rounding_value)
			# 	new_value = new_exp_df[channel].iloc[n]
			# 	diff = round(orig_avg - new_value,rounding_value)
			# 	if abs(diff) > 2.*rounding_value:
			# 		print(n)
			# 		print(diff)
			# 		print(orig_avg, new_value)

	if exp_des['Speed'][exp] == 'high':
		all_exp_data[exp] = new_exp_df

	all_exp_FED_data[exp] = all_exp_data[exp].reset_index()

	# Output time synced dictionary for FED

	# Adjust time to be every 2 seconds regardless of the drift. 
	time = all_exp_FED_data[exp]['Time'].tolist()

	if exp_des['Speed'][exp] == 'high':
		time = time[::2]
		all_exp_FED_data[exp] = all_exp_FED_data[exp][::2]

	elif exp_des['Speed'][exp] == 'low':
		if exp_des['House'][exp] == 'a':
			time = time[::2]
			all_exp_FED_data[exp] = all_exp_FED_data[exp][::2]

	if time[0] % 2 != 0:
		time[0] = time[0]-1

	if time[-1] % 2 != 0:
		time[-1] = time[-1]+1
	
	new_time = np.arange(time[0], time[-1], 2)

	if len(new_time) < len(all_exp_FED_data[exp].index):		
		add_time = np.arange(new_time[-1]+2, new_time[-1]+(len(all_exp_FED_data[exp].index)-len(new_time)+2)*2,2)
		new_time = np.append(new_time, add_time)

	all_exp_FED_data[exp]['Time'] = new_time[:len(all_exp_FED_data[exp].index)]

	all_exp_FED_data[exp].set_index('Time', inplace=True)

	print (exp + ' Read')

pickle.dump(all_exp_data, open (data_location + 'all_exp_data.dict' , 'wb'))
pickle.dump(all_exp_FED_data, open(data_location + 'all_exp_FED_data.dict' , 'wb'))

print ('\n')
print ('-------------- all_exp_data.dict dumped to data folder ------------------')
print ('-------------- all_exp__FED_data.dict dumped to data folder ------------------')

# Read in all flow data to dictionary 'all_flow_data' with dataframe value = 'Experiment_X_Data' save to pickle file all_flow_data.dict
print ('Reading in Flow Data \n')

first_flow_time = pd.read_csv('../3_Info/First_Flow_Time.csv').set_index('Experiment')

all_flow_data = {}

for exp in exp_des.index.values:

	if os.path.isfile((data_location + exp[:-4] + 'Flow.csv')):

		all_flow_data[exp] = pd.read_csv(data_location + exp[:-4] + 'Flow.csv')
		all_flow_data[exp]['Time'] = [datetime.datetime.strptime(t, '%M:%S.%f') for t in all_flow_data[exp]['Time']]
		all_flow_data[exp]['Time'] = [(t-all_flow_data[exp]['Time'][0]).total_seconds() for t in all_flow_data[exp]['Time']]

		flow_time = all_flow_data[exp]['Time'][np.argmax(all_flow_data[exp]['GPM']>10)]
		
		all_flow_data[exp]['Time'] = all_flow_data[exp]['Time'] + (first_flow_time['First_Flow'][exp] - flow_time)

		all_flow_data[exp].set_index('Time', inplace=True)
		
		all_flow_data[exp] = all_flow_data[exp][::10]

		print (exp[:-4].replace('_', ' ') + 'Flow Read')

pickle.dump(all_flow_data, open (data_location + 'all_flow_data.dict' , 'wb'))

print ('\n')
print ('-------------- all_exp_events.dict dumped to data folder ------------------')

