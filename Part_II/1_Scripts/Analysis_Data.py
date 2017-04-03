import pandas as pd
import os
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt

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

#Read in all experiment events to dictionary 'all_exp_events' with dataframe value = 'Experiment_X_Event'
print ('Reading in Experiment Events \n')
all_exp_events = {}

for exp in exp_des.index.values:
	exp = exp[:-4] + 'Events'
	events = pd.read_csv(events_location + exp + '.csv')
	all_exp_events[exp] = events.set_index('Event')
	print (exp + ' Read')
#Read in all experiment data to dictionary 'all_exp_data' with the dataframe value = 'Experiment_X_Data'
print ('\n')
print ('Reading in Experiment Data \n')

all_exp_data = {}
avg_first_event = pd.DataFrame()
ignition_seconds ={}

for exp in exp_des.index.values:

	data = pd.read_csv(data_location +  exp + '.csv')
	
	all_exp_data[exp] = pd.DataFrame()

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
	event = datetime.datetime.strptime(all_exp_events[exp[:-4]+'Events']['Time'][0], '%H:%M:%S')
	first_event = datetime.datetime.strptime(all_exp_events[exp[:-4]+'Events']['Time'][1], '%H:%M:%S')

	avg_first_event[exp] = [(first_event - event).total_seconds()]

	#Adjust time to be every 2 seconds regardless of the drift. 
	time = [int((t - event).total_seconds()) for t in time]
	
	if time[0] % 2 != 0:
		time[0] = time[0]+1
	
	new_time = np.arange(time[0], time[-1], 2)

	if len(new_time) < len(data.index):		
		add_time = np.arange(new_time[-1]+2, new_time[-1]+(len(data.index)-len(new_time)+2)*2,2)
		new_time = np.append(new_time, add_time)

	data['Time'] = new_time[:len(data.index)]

	all_exp_data[exp] = data.set_index('Time')
	print(exp + ' Read')

# # -------------------------------Calculate and output Repeatibility Data-------------------------------
# running_comp = {}

# output_location = '../2_Data/Repeatibility_Data'

# for vent in vent_info.columns:
# 	comp_data = pd.DataFrame({'Time':np.arange(-60,-5,2)})
# 	comp_data = comp_data.set_index('Time')

# 	for exp in vent_info[vent].dropna():

# 		# if exp not in experiments:
# 		# 	continue

# 		data = all_exp_data[exp]

# 		if exp_des['Speed'][exp] == 'high':
# 				data = data[-60:-5:20]

# 		if exp_des['Speed'][exp] == 'low':
# 			if exp_des['House'][exp] == 'a':
# 				data = data[-60:-5:2]
# 			if exp_des['House'][exp] == 'b':
# 				data = data[-60:-5]

# 		data.name = exp

# 		data = data.reset_index(drop=True)

# 		if len(data) != 28:
# 			data = data[0:28]

# 		data.index = np.arange(-60,-5,2)

# 		if vent not in running_comp:
# 			running_comp[vent] = {}

# 		running_comp[vent][exp] = data



# repeatability_data  = {}

# if not os.path.exists(output_location):
# 	os.makedirs(output_location)

# for vent in vent_info.columns.values:

# 	if vent not in repeatability_data:
# 		repeatability_data[vent] = {}

# 	for exp in vent_info[vent].dropna():

# 		Experiment_Data = pd.DataFrame()

# 		for channel_group in channels_grouped.groups:

# 			group_values = pd.DataFrame()

# 			if channel_group in groups_to_skip:
# 				continue

# 			for channel in channels_grouped.get_group(channel_group).index.values:

# 				if channel not in running_comp[vent][exp].keys():
# 					continue 

# 				if channel in channels_to_skip:
# 					continue

# 				if exp_des['House'][exp] == 'a':
# 					scalefactor = 'ScaleFactor_A'
# 					Transport_Time = 'Transport_Time_A'

# 				if exp_des['House'][exp] == 'b':
# 					scalefactor = 'ScaleFactor_B'
# 					Transport_Time = 'Transport_Time_B'

# 				value = pd.DataFrame(running_comp[vent][exp][channel])
		
# 				value = value*channel_list[scalefactor][channel]+channel_list['Offset'][channel]

# 				group_values = pd.concat([group_values, value], axis =1)

# 			if channel_list['Type'][channel] == 'Temperature':
# 				group_values = group_values.mean(axis=1)

# 			if exp not in repeatability_data[vent]:
# 				repeatability_data[vent][exp] = {}

# 			# print (channel_list['Type'][channel])

# 			if channel_list['Type'][channel] == 'Temperature':
# 				repeatability_data[vent][exp][channel_group]=group_values.mean()
# 			# elif channel_list['Type'][channel] == 'Gas':
# 			# 	for chan in group_values:
# 			# 		repeatability_data[vent][exp][chan]=group_values[chan].mean()
# 			elif 'Flux' in channel_list['Type'][channel]:
# 				for chan in group_values:
# 					repeatability_data[vent][exp][chan]=group_values[chan].mean()

# 			# repeatability_data[vent][exp][channel_group]=group_values.mean()
# 	# exit()

# 	repeatability_data_csv = pd.DataFrame.from_dict(repeatability_data[vent])
# 	repeatability_data_csv = repeatability_data_csv.reset_index()
# 	repeatability_data_csv.rename(columns={'index':'Location'}, inplace=True)

# 	data_types = []
# 	for location in repeatability_data_csv['Location']:
# 		if 'Temps' in location:
# 			data_types = data_types + ['Temperature']
# 		elif 'HF' in location:
# 			data_types = data_types + ['Heat Flux']
# 		elif 'Carbon' in location:
# 			data_types = data_types + ['Carbon Monoxide']
# 		elif 'CO2' in location:
# 			data_types = data_types + ['Carbon Dioxide']
# 		elif 'O2' in location:
# 			data_types = data_types + ['Oxygen']

# 	repeatability_data_csv['Type'] = data_types

# 	repeatability_data_csv.to_csv(output_location + '/' + vent + '.csv', index=False)
 

# # -------------------------------Calculate and output FED Data-------------------------------
output_location = '../2_Data/FED'

if not os.path.exists(output_location):
	os.makedirs(output_location)

Victim_Locations = ['1','2','3','4']

all_FED = {}
all_FED_Temp = {}

print ('\n')
print ('Calculating FED')

for vent_config in vent_info:
	for victim_loc in Victim_Locations:
		for gas in ['COV', 'CO2V', 'O2V']:
			plt.figure(vent_config + '_Victim_' +  victim_loc + '_' + gas)

for exp in exp_des.index.values:
	print (exp + 'FED Calculated')

	if exp_des['Speed'][exp] == 'high':
			# s = all_exp_data[exp].index.to_series().astype(int)
			# all_exp_data[exp] = all_exp_data[exp].groupby(s).std().set_index(s.index[::10])
			sample_speed = 1/(60*100)

	if exp_des['Speed'][exp] == 'low':
		if exp_des['House'][exp] == 'a':
			sample_speed = 1/60
		if exp_des['House'][exp] == 'b':
			sample_speed = 1/30
	
	if exp not in all_FED:
		all_FED[exp] = pd.DataFrame()
	
	if exp not in all_FED_Temp:
		all_FED_Temp[exp] = {}

	exp_FED = pd.DataFrame({'Time':all_exp_data[exp].index.values})
	exp_FED = exp_FED.set_index('Time')

	exp_FED_Temp = pd.DataFrame({'Time':all_exp_data[exp].index.values})
	exp_FED_Temp = exp_FED_Temp.set_index('Time')

	for victim_loc in Victim_Locations:
		for chan in ['COV', 'CO2V', 'O2V', 'HFS']:
			if victim_loc + chan in channels_to_skip[exp]:
				continue

			#Skip the victim #2 for times when the bedroom door was accidently left open.
			if exp in ['Experiment_1_Data', 'Experimeng_14_Data']:
				if victim_loc == '2':
					continue

			scalefactor = channel_list['ScaleFactor_' + exp_des['House'][exp].upper()][victim_loc+chan]
			
			offset = channel_list['Offset'][victim_loc+chan]

			#Correct to Zero from background data
			if chan in ['COV', 'CO2V']:
				val = all_exp_data[exp][victim_loc + chan] - all_exp_data[exp][victim_loc + chan][0:60].mean()
			else:
				val = all_exp_data[exp][victim_loc + chan]

			if chan != 'HFS':
				if transport_times['Victim_' + victim_loc + '_' + exp_des['House'][exp].upper()][exp] == 'Bad_Data':
					continue
				else:
					transport = int(transport_times['Victim_' + victim_loc + '_' + exp_des['House'][exp].upper()][exp])		
					if transport % 2 != 0:
						transport = transport - 1

			#Calculate Value
			val = val * scalefactor + offset

			if chan != 'HFS':
				#Adjust for transport time
				val.index = val.index-transport

			if chan == 'O2V':
				val = val + (20.95 - val[0:60].mean())
			if all_FED[exp].empty:
				all_FED[exp][victim_loc+chan] = val
			else:
				all_FED[exp] = pd.concat([all_FED[exp], val], axis = 1)

			for vent_config in vent_info:
				if exp in vent_info[vent_config].dropna().tolist():
					plt.figure(vent_config + '_Victim_' +  victim_loc + '_' + chan)
					plt.plot(all_FED[exp][victim_loc + chan], label = exp.replace('_', ' '))

		if all_FED[exp].empty:
			continue
		
		time_step = (all_FED[exp].index[1]-all_FED[exp].index[0])/60 #In minutes

		#Calculate FED CO and add in CO2 Correction
		if victim_loc + 'COV' in all_FED[exp]:
			FED = (3.317e-5*(all_FED[exp][victim_loc+'COV']**1.036)*25*time_step)/30 #Purser SFPE 2-117 for a V of light work (25L/min) & D (30 %COHb)


		if victim_loc + 'O2V' in all_FED[exp]:
			t_io2 = np.exp(8.13-0.54*(20.9-all_FED[exp][victim_loc +'O2V']))
			FED_O2 = ((20.95-all_FED[exp][victim_loc +'O2V'])*time_step/((20.95-all_FED[exp][victim_loc +'O2V'])*t_io2))

		if victim_loc + 'CO2V' in all_FED[exp]:
			t_ico2 = np.exp(6.1623-0.5189*all_FED[exp][victim_loc + 'CO2V'])
			FED_CO2 = ((all_FED[exp][victim_loc + 'CO2V']*time_step)/(all_FED[exp][victim_loc + 'CO2V']*t_ico2))
			
			CO2per_test = all_FED[exp][victim_loc + 'CO2V'].tolist()

			CO2_corr = np.zeros(len(FED))

			for c in np.arange(0,len(FED)):
				if CO2per_test[c] >= 2:
					CO2_corr[c] = np.exp(CO2per_test[c]/5)
				else: 
					CO2_corr[c] = 1 
		
		# print('Victim ' + victim_loc)
		try:
			FED = (FED_O2 + FED) * CO2_corr
			del CO2_corr
		except NameError:
			# print ('Value Missing')
			continue

		FED_sum = []

		FED_sum = [FED[0:val].sum() for val in np.arange(0,len(FED))]

		FED_sum = pd.DataFrame({'Time':FED.index.values, 'FED_Vic' + victim_loc: FED_sum})
		FED_sum = FED_sum.set_index('Time')

		if exp_FED.empty:
			exp_FED = FED_sum
		else:
			exp_FED = pd.concat([exp_FED,FED_sum], axis=1)
		
		#Calculate Temp FED (SFPE Purser 2-145) using data from LC_50 for fatal heat dose.
		if victim_loc + 'HFS' in all_FED[exp]:
			t_rad = (16.7)/(all_FED[exp][victim_loc+'HFS']**1.33)

			F_rad = 1/t_rad

			FED_Temp = (F_rad)*time_step

			FED_Temp_sum = []

			FED_Temp_sum = [FED_Temp[0:val].sum() for val in np.arange(0,len(FED_Temp))]

			FED_Temp_sum = pd.DataFrame({'Time':FED_Temp.index.values, 'FED_Temp_Vic' + victim_loc: FED_Temp_sum})
			FED_Temp_sum = FED_Temp_sum.set_index('Time')

			if exp_FED_Temp.empty:
				exp_FED_Temp = FED_Temp_sum
			else:
				exp_FED_Temp = pd.concat([exp_FED_Temp,FED_Temp_sum], axis=1)

	if exp_FED.empty:
		all_FED.pop(exp)
	else:
		all_FED[exp] = exp_FED

	if exp_FED_Temp.empty:
		all_FED_Temp.pop(exp)
	else:
		all_FED_Temp[exp] = exp_FED_Temp

if not os.path.exists('../0_Images/Results/Script_Figures/Gas_Compare/'):
	os.makedirs('../0_Images/Results/Script_Figures/Gas_Compare/')

for vent_config in vent_info:
	event_time = np.average([avg_first_event[t] for t in vent_info[vent_config].dropna()])
	min_time = np.min([avg_first_event[t] for t in vent_info[vent_config].dropna()])
	max_time = np.max([avg_first_event[t] for t in vent_info[vent_config].dropna()])
	if vent_config == 'Single_Vent':
		print(event_time)
		exit()
		
	for victim_loc in Victim_Locations:


		for gas in ['COV', 'CO2V', 'O2V']:
			plt.figure(vent_config + '_Victim_' +  victim_loc + '_' + gas)

			if gas == 'O2V':
				plt.legend(loc = 'lower left')
			else:
				plt.legend(loc = 'upper left')
			
			plt.title(vent_config.replace('_', ' ') + ' Victim ' + victim_loc + ' ' + gas)
			plt.xlabel('Time (seconds)')
	
			if gas == 'COV':
				plt.ylabel('CO (PPM)')
				plt.ylim([0,50000])
			else:
				plt.ylabel('Percent ' + gas[:-1])
				plt.ylim([0,25])

			plt.xlim([0,600])
			plt.axvline(0, color = 'black')
			plt.axvline(event_time, color = 'black')
			plt.axvspan(min_time, max_time, alpha=0.5, color='grey')
			plt.savefig('../0_Images/Results/Script_Figures/Gas_Compare/' + vent_config + '_Victim_' + victim_loc + '_' + gas + '.pdf')
			plt.close()		

plt.close('all')

#----------------------------Uncomment to plot FED Charts by Victim, Attack, and Vent Config-----------------------
if not os.path.exists('../0_Images/Results/Script_Figures/FED_Line/'):
	os.makedirs('../0_Images/Results/Script_Figures/FED_Line/')

for compare in FED_info:
	# print (compare)
	for vic in Victim_Locations:
		victim = 'FED_Vic' + vic
		# print(victim)
		for exp in FED_info[compare].dropna():
			# print(exp)
			if exp not in all_FED:
				continue
			if victim not in all_FED[exp]:
				continue

			p = plt.plot(all_FED[exp][victim], label=exp.replace('_', ' '))
		plt.title(compare.replace('_',' '))
		plt.legend()
		plt.savefig('../0_Images/Results/Script_Figures/FED_Line/' + compare + '_' + victim + '.pdf')
		plt.close('all')

#Create Data for each victim package during each experiment at the time of FD intervention
all_FED_csv = pd.DataFrame({'Locations':['FED_Vic1','FED_Vic2','FED_Vic3','FED_Vic4']})
all_FED_csv.set_index('Locations', inplace = True)

all_FED_Temp_csv = pd.DataFrame({'Locations':['FED_Temp_Vic1','FED_Temp_Vic2','FED_Temp_Vic3','FED_Temp_Vic4']})
all_FED_Temp_csv.set_index('Locations', inplace = True)

for exp in all_FED:
	exp_FED_values = pd.DataFrame({'Locations':all_FED[exp].columns.values, exp:[all_FED[exp][col][0] for col in all_FED[exp].columns.values]})
	exp_FED_values.set_index('Locations', inplace = True)
	all_FED_csv = pd.concat([all_FED_csv, exp_FED_values], axis=1)

all_FED_csv.reset_index(inplace = True)
all_FED_csv.to_csv(output_location + '/Intervention_FED.csv', index = False)

for exp in all_FED_Temp:
	exp_FED_values = pd.DataFrame({'Locations':all_FED_Temp[exp].columns.values, exp:[all_FED_Temp[exp][col][0] for col in all_FED_Temp[exp].columns.values]})
	exp_FED_values.set_index('Locations', inplace = True)
	all_FED_Temp_csv = pd.concat([all_FED_Temp_csv, exp_FED_values], axis = 1)

all_FED_Temp_csv.reset_index(inplace = True)
all_FED_Temp_csv.to_csv(output_location + '/Intervention_FED_Temp.csv', index = False)


#Create Data for each victim package during each experiment during the 2min post intervention. 
all_FED_csv = pd.DataFrame({'Locations':['FED_Vic1','FED_Vic2','FED_Vic3','FED_Vic4']})
all_FED_csv.set_index('Locations', inplace = True)

all_FED_Temp_csv = pd.DataFrame({'Locations':['FED_Temp_Vic1','FED_Temp_Vic2','FED_Temp_Vic3','FED_Temp_Vic4']})
all_FED_Temp_csv.set_index('Locations', inplace = True)

for exp in all_FED:
	exp_FED_values = pd.DataFrame({'Locations':all_FED[exp].columns.values, exp:[all_FED[exp][col][120]-all_FED[exp][col][0] for col in all_FED[exp].columns.values]})
	exp_FED_values.set_index('Locations', inplace = True)
	all_FED_csv = pd.concat([all_FED_csv, exp_FED_values], axis = 1)

all_FED_csv.reset_index(inplace = True)
all_FED_csv.to_csv(output_location + '/Intervention_Plus60_FED.csv', index = False)

for exp in all_FED_Temp:
	exp_FED_values = pd.DataFrame({'Locations':all_FED_Temp[exp].columns.values, exp:[all_FED_Temp[exp][col][120]-all_FED_Temp[exp][col][0] for col in all_FED_Temp[exp].columns.values]})
	exp_FED_values.set_index('Locations', inplace = True)
	all_FED_Temp_csv = pd.concat([all_FED_Temp_csv, exp_FED_values], axis = 1)

all_FED_Temp_csv.reset_index(inplace = True)
all_FED_Temp_csv.to_csv(output_location + '/Intervention_Plus60_FED_Temp.csv', index = False)

# for exp in exp_des.index.values:
# 	time_start = datetime.datetime.strptime(all_exp_events[exp[:-4]+'Events']['Time'][1], '%H:%M:%S')
# 	time_end = datetime.datetime.strptime(all_exp_events[exp[:-4]+'Events']['Time'][-2], '%H:%M:%S')
# 	print ((time_end - time_start).total_seconds())
