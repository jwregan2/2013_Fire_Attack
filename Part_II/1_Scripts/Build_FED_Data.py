# ***************************** Run notes *****************************
# Must be run affter Build_Data_Dictionary.py to build pickle file of data.
# Will build three dictionary files [FED_Gas.dict, FED_Temp_Flux.dict, FED_Temp_Conv.dict]
# Each file is the Fractional Effective Dose for the given quantity where FED_Gas uses the Oxygen, CO2 and CO,
# Temp_Flux is using the equation in the SFPE Handbook (2-144) for total energy flux to achive LC_50
# with a known total flux exposure from a schmidt bolter gauge, and Temp_Conv is using the gas temperature
# strictily based on the convective transfer.

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
FED_info = pd.read_csv('../3_Info/FED_Info.csv')

exp_des = pd.read_csv('../3_Info/Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

for exp in exp_des.index.values:
	channels_to_skip[exp] = exp_des['Excluded Channels'][exp].split('|')

#Read in pickle file for data
all_exp_data = pickle.load( open( data_location + 'all_exp_FED_data.dict', 'rb' ) )
all_exp_events = pickle.load( open (events_location + 'all_exp_events.dict', 'rb'))

output_location = '../2_Data/FED/'

if not os.path.exists(output_location):
	os.makedirs(output_location)

Victim_Locations = ['1','2','3','4','5']

FED_Gas = {}
FED_Temp_Flux = {}
FED_Temp_Conv = {}

print ('\n')
print ('Calculating FED')

for exp in exp_des.index.values:
	print (exp + ' Calculating FED')

	if exp not in FED_Gas:
		FED_Gas[exp] = pd.DataFrame({'Time':all_exp_data[exp].index.tolist()}).set_index('Time')
	
	if exp not in FED_Temp_Flux:
		FED_Temp_Flux[exp] = pd.DataFrame({'Time':all_exp_data[exp].index.tolist()}).set_index('Time')

	if exp not in FED_Temp_Conv:
		FED_Temp_Conv[exp] = pd.DataFrame({'Time':all_exp_data[exp].index.tolist()}).set_index('Time')

	for victim_loc in Victim_Locations:

		time_step = (all_exp_data[exp].index.tolist()[1] - all_exp_data[exp].index.tolist()[0])/60 #Timestep in minutes from index of all_exp_data from particular experiment

		#Calculate FED CO and add in CO2 Correction
		if victim_loc + 'COV' in all_exp_data[exp]:
			if victim_loc + 'COV' not in channels_to_skip[exp]:
				FED = (3.317e-5*(all_exp_data[exp][victim_loc+'COV']**1.036)*25*time_step)/30 #Purser SFPE 2-117 for a V of light work (25L/min) & D (30 %COHb)


		if victim_loc + 'O2V' in all_exp_data[exp]:
			if victim_loc + 'O2V' not in channels_to_skip[exp]:
				t_io2 = np.exp(8.13-0.54*(20.9-all_exp_data[exp][victim_loc +'O2V']))
				FED_O2 = ((20.95-all_exp_data[exp][victim_loc +'O2V'])*time_step/((20.95-all_exp_data[exp][victim_loc +'O2V'])*t_io2))
			
			#For victim 4, experiment 1 ignore the FED for the oxygen sensor.
			if exp == 'Experiment_1_Data' and victim_loc == '4':
				FED_O2 = np.zeros(len(all_exp_data[exp][victim_loc+'O2V']))

		if victim_loc + 'CO2V' in all_exp_data[exp]:
			if victim_loc + 'CO2V' not in channels_to_skip[exp]:
				t_ico2 = np.exp(6.1623-0.5189*all_exp_data[exp][victim_loc + 'CO2V'])
				FED_CO2 = ((all_exp_data[exp][victim_loc + 'CO2V']*time_step)/(all_exp_data[exp][victim_loc + 'CO2V']*t_ico2))
				
				CO2per_test = all_exp_data[exp][victim_loc + 'CO2V'].tolist()

				CO2_corr = np.zeros(len(FED))

				for c in np.arange(0,len(FED)):
					if CO2per_test[c] >= 2:
						CO2_corr[c] = np.exp(CO2per_test[c]/5)
					else: 
						CO2_corr[c] = 1 

		try:
			FED = (FED_O2 + FED) * CO2_corr
			del CO2_corr
			FED_Gas[exp]['Victim_'+victim_loc] = [FED[0:val].sum() for val in np.arange(0,len(FED))]
		except NameError:
			pass
		
		#Calculate Temp FED (SFPE Purser 2-144) using data from LC_50 for fatal heat dose.
		if victim_loc + 'HFS' in all_exp_data[exp]:
			if victim_loc + 'HFS' not in channels_to_skip[exp]:
				t_rad = 16.7/(all_exp_data[exp][victim_loc+'HFS']**1.33)
				FED_flux = (1/t_rad)*time_step
				FED_Temp_Flux[exp]['Victim_'+ victim_loc] = [FED_flux[0:val].sum() for val in np.arange(0,len(FED_flux))]

		#Calculate TEMP FED based on gas temperature (SFPE Purser 2-145) for a fatal dose
		if victim_loc + 'TCV1' in all_exp_data[exp]:
			if victim_loc + 'TCV1' not in channels_to_skip[exp]:
				all_exp_data[exp][victim_loc + 'TCV1'] = (all_exp_data[exp][victim_loc + 'TCV1']-32)/1.8

				#Only add FED where temperature is above 50C based on data from Thermal Tolerance for humans at rest.
				FED_conv = np.zeros(len(all_exp_data[exp][victim_loc + 'TCV1']))

				for f in all_exp_data[exp][victim_loc + 'TCV1'].index.values:

					if all_exp_data[exp][victim_loc + 'TCV1'][f] > 50:
						FED_conv[int(f/2)] = (1/(2e18 * all_exp_data[exp][victim_loc + 'TCV1'][f]**-9.0403 + 1e8 * all_exp_data[exp][victim_loc + 'TCV1'][f]**-3.10898))*time_step

				FED_Temp_Conv[exp]['Victim_' + victim_loc] = [FED_conv[0:val].sum() for val in np.arange(0,len(FED_conv))]

		try:
			del FED
			del FED_O2
			del FED_CO2
		except NameError:
			pass

pickle.dump(FED_Gas, open (output_location + 'FED_Gas.dict' , 'wb'))
print ('-------------- FED_Gas.dict dumped to ../Data/FED folder ------------------')

pickle.dump(FED_Temp_Flux, open (output_location + 'FED_Temp_Flux.dict' , 'wb'))
print ('-------------- FED_Temp_Flux.dict dumped to ../Data/FED folder ------------------')

pickle.dump(FED_Temp_Conv, open (output_location + 'FED_Temp_Conv.dict' , 'wb'))
print ('-------------- FED_Temp_Conv.dict dumped to ../Data/FED folder ------------------')


