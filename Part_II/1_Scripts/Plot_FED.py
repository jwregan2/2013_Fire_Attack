# *********************************** Run Notes *********************************
# Must be run after Building_Data_Dictionary.py and Build_FED_Data.py. Script will
# plot the FED values over time for the gas, conv and flux values for each of the vent
# configurations based on the victim location. . Additionally it will plot the baseline FED 
# for each of the vent cofigurations for each of the delayed water cases. 

import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt
import matplotlib.axes as ax
import os
import pickle
from itertools import cycle
import matplotlib.transforms as mtransforms
from pylab import * 

data_location = '../2_Data/FED/'
events_location = '../3_Info/Events/'

all_exp_events = pickle.load(open(events_location + 'all_exp_events.dict', 'rb'))
all_exp_data = pickle.load(open('../2_Data/all_exp_FED_data.dict', 'rb'))
FED_Gas = pickle.load(open(data_location + 'FED_Gas.dict', 'rb'))
FED_Temp_Flux = pickle.load(open(data_location + 'FED_Temp_Flux.dict', 'rb'))
FED_Temp_Conv = pickle.load(open(data_location + 'FED_Temp_Conv.dict', 'rb'))
vent_info = pd.read_csv('../3_Info/Vent_Info.csv')

victims = ['Victim_1', 'Victim_2', 'Victim_3', 'Victim_4', 'Victim_5']

#Define color pallet
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Define RGB values in pallet 
for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b / 255.)

# ---------------------------------Plot Baseline Data With No Intervention----------------------------- 

output_location = '../0_Images/Script_Figures/FED/FED_Base/'

experiments = ['Experiment_1_Data', 'Experiment_12_Data', 'Experiment_17_Data']

dose_types = {'Toxic_Gas':FED_Gas, 'Convective':FED_Temp_Conv, 'Total_Flux':FED_Temp_Flux}

if not os.path.exists(output_location):
	os.makedirs(output_location)

marker = {'Toxic_Gas':"s", 'Convective':"o", 'Total_Flux':"d"}
color = {'Experiment_1_Data':tableau20[0], 'Experiment_12_Data':tableau20[1], 'Experiment_17_Data':tableau20[2]}

for vic in victims:
	
	# Create figure
	fig = plt.figure()
	fig.set_size_inches(8, 6)

	for exp in experiments:

		if exp == 'Experiment_1_Data' and vic == 'Victim_2':
			continue
		
		for dose_type in dose_types:
			if vic in dose_types[dose_type][exp]:
				end_time = all_exp_events[exp[:-4]+'Events']['Time_Seconds']['Suppression Crew Enters']
				data = dose_types[dose_type][exp][vic].ix[:end_time]
				data.index = data.index/60
				plt.plot(data, label = 'Exp ' + exp[11:-5] + ' ' + dose_type.replace('_',' '), lw = 2, marker = marker[dose_type], 
					color = color[exp], markevery=20)


				if dose_type == 'Total_Flux':
					fatal_time = data[data > 1].index
					if fatal_time.empty == False:
						print (exp + ',' + vic + ',' + dose_type + ',' + str(data[data > 1].index[0]))
				if dose_type == 'Toxic_Gas':
					fatal_time = data[data > 3].index
					if fatal_time.empty == False:
						print (exp + ',' + vic + ',' + dose_type + ',' + str(data[data > 3].index[0]))
				if dose_type == 'Convective':
					fatal_time = data[data > 1].index
					if fatal_time.empty == False:
						print (exp + ',' + vic + ',' + dose_type + ',' + str(data[data > 1].index[0]))

	L = plt.legend()
	num_entries = len(L.get_texts())

	plt.ylim([0,3])
	plt.axhline(1, color = 'black', lw = 2)
	plt.title(vic.replace('_', ' '), fontsize = 20)
	# plt.xlim([0,all_exp_events[exp[:-4]+'Events']['Time_Seconds']['Attack Team Enters']/60])
	plt.ylabel('Fractional Effective Dose', fontsize = 18)
	plt.xlabel('Time (min)', fontsize = 18)
	plt.xticks(fontsize = 18)
	plt.yticks(fontsize = 18)
	
	pos_legend = 1 - (num_entries*.1025)

	plt.legend(bbox_to_anchor=(1.005  , 1 - pos_legend/2), loc='upper left', ncol=1, fontsize = 16)
	plt.subplots_adjust(top= 0.75, bottom=0.15, right=0.62)
	plt.savefig(output_location + vic + '.pdf')
	plt.close('all')

# -----------------------Plot Average of FED Gas based on Vent to FD Intervention----------------------
output_location = '../0_Images/Script_Figures/FED/FED_Avg_Gas/'

if not os.path.exists(output_location):
    os.makedirs(output_location)

events = pd.DataFrame()

interventions = pd.DataFrame({'Vent_Config':vent_info.columns.values, 'Time':np.arange(len(vent_info.columns.values))}).set_index('Vent_Config')

# Determine the minimum intervention time
for vent in vent_info:
	for exp in vent_info[vent].dropna():
		events[exp] = all_exp_events[exp[:-4]+'Events']['Time_Seconds']
	interventions['Time'][vent] = min(events.ix[1])

values = pd.DataFrame()

for vent in vent_info:

	# Create figure
	fig = plt.figure()
	fig.set_size_inches(8, 6)

	# Plot style - cycle through 20 color pallet and define markers to cycle through
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	for vic in victims:

		values = pd.DataFrame()
		
		for exp in vent_info[vent].dropna():
			if vic not in FED_Gas[exp]:
				continue
			
			#Skip Experiment 1 and 14, Victim 2 where door left open. 
			if exp in ['Experiment_1_Data','Experiment_14_Data'] and vic == 'Victim_2':
				continue

			values[exp] = FED_Gas[exp][vic]
		
		values = values.ix[0:interventions['Time'][vent]]
		
		if not values.empty:
			p = plt.plot(values.index/60, values.mean(axis=1), marker = next(plot_markers), markevery=20, label = vic.replace('_', ' '), lw = 2)
			std = values.std(axis=1)
			min_values = (values.mean(axis=1)-std).tolist()
			for v in np.arange(len(min_values)):
				if min_values[v] < 0:
					min_values[v] = 0
			max_values = values.mean(axis=1)+std

			plt.fill_between(values.index.values/60, max_values, min_values, color=p[0].get_color(), alpha=0.15)
	
	plt.ylim([0,3])
	plt.xlim([0,interventions['Time'][vent]/60])
	plt.xticks(fontsize = 18)
	plt.yticks(fontsize = 18)
	plt.ylabel('Fractional Effective Dose', fontsize = 18)
	plt.xlabel('Time (min)', fontsize = 18)
	plt.legend(bbox_to_anchor=(1.01, 0.75), loc='upper left', ncol=1, fontsize = 18)
	plt.subplots_adjust(bottom=0.15, right=0.70)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

# ---------------------------------Plot Average of FED Temp Conv based on Vent to FD Intervention----------------------------- 
output_location = '../0_Images/Script_Figures/FED/FED_Avg_Temp_Conv/'

if not os.path.exists(output_location):
    os.makedirs(output_location)

events = pd.DataFrame()

interventions = pd.DataFrame({'Vent_Config':vent_info.columns.values, 'Time':np.arange(len(vent_info.columns.values))}).set_index('Vent_Config')

# Determine the minimum intervention time
for vent in vent_info:
	for exp in vent_info[vent].dropna():
		events[exp] = all_exp_events[exp[:-4]+'Events']['Time_Seconds']
	interventions['Time'][vent] = min(events.ix[1])
	
	print ('The earliest intervention in the ' + vent + ' case was ' +  str(interventions['Time'][vent]) + ' seconds.')

values = pd.DataFrame()

for vent in vent_info:

	# Create figure
	fig = plt.figure()
	fig.set_size_inches(8, 6)

	# Plot style - cycle through 20 color pallet and define markers to cycle through
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	for vic in victims:

		values = pd.DataFrame()
		
		for exp in vent_info[vent].dropna():
			if vic not in FED_Temp_Conv[exp]:
				continue
			
			#Skip Experiment 1 and 14, Victim 2 where door left open. 
			if exp in ['Experiment_1_Data','Experiment_14_Data'] and vic == 'Victim_2':
				continue
			
			values[exp] = FED_Temp_Conv[exp][vic]
		
		values = values.ix[0:interventions['Time'][vent]]
		
		if not values.empty:
			p = plt.plot(values.index/60, values.mean(axis=1), marker = next(plot_markers), markevery=20, label = vic.replace('_', ' '), lw = 2)
			std = values.std(axis=1)
			min_values = (values.mean(axis=1)-std).tolist()
			for v in np.arange(len(min_values)):
				if min_values[v] < 0:
					min_values[v] = 0
			max_values = values.mean(axis=1)+std

			# plt.plot(max_values, color = 'black')
			# plt.plot(values.index.values, min_values, color = 'black')
			plt.fill_between(values.index.values/60, max_values, min_values, color=p[0].get_color(), alpha=0.15)
	
	plt.ylim([0,1])
	plt.xlim([0,interventions['Time'][vent]/60])
	plt.xticks(fontsize = 18)
	plt.yticks(fontsize = 18)
	plt.ylabel('Fractional Effective Dose', fontsize = 18)
	plt.xlabel('Time (min)', fontsize = 18)
	plt.legend(bbox_to_anchor=(1.01, 0.75), loc='upper left', ncol=1, fontsize = 18)
	plt.subplots_adjust(bottom=0.15, right=0.70)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

# ---------------------------------Plot Average of FED Temp Flux Gas based on Vent to FD Intervention----------------------------- 
output_location = '../0_Images/Script_Figures/FED/FED_Avg_Temp_Flux/'

if not os.path.exists(output_location):
    os.makedirs(output_location)

events = pd.DataFrame()

interventions = pd.DataFrame({'Vent_Config':vent_info.columns.values, 'Time':np.arange(len(vent_info.columns.values))}).set_index('Vent_Config')

# Determine the minimum intervention time
for vent in vent_info:
	for exp in vent_info[vent].dropna():
		events[exp] = all_exp_events[exp[:-4]+'Events']['Time_Seconds']
	interventions['Time'][vent] = min(events.ix[1])

values = pd.DataFrame()

for vent in vent_info:

	# Create figure
	fig = plt.figure()
	fig.set_size_inches(8, 6)

	# Plot style - cycle through 20 color pallet and define markers to cycle through
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	for vic in victims:

		values = pd.DataFrame()
		
		for exp in vent_info[vent].dropna():
			if vic not in FED_Temp_Flux[exp]:
				continue
			
			#Skip Experiment 1 and 14, Victim 2 where door left open. 
			if exp in ['Experiment_1_Data','Experiment_14_Data'] and vic == 'Victim_2':
				continue

			#Skip Experiment 16 Victim 5 as the scale seems off. 
			if exp == 'Experiment_16_Data' and vic == 'Victim_5':
				continue

			values[exp] = FED_Temp_Flux[exp][vic]
		
		values = values.ix[0:interventions['Time'][vent]]
		
		if not values.empty:
			p = plt.plot(values.index/60, values.mean(axis=1), marker = next(plot_markers), markevery=20, label = vic.replace('_', ' '), lw = 2)
			std = values.std(axis=1)
			min_values = (values.mean(axis=1)-std).tolist()
			for v in np.arange(len(min_values)):
				if min_values[v] < 0:
					min_values[v] = 0
			max_values = values.mean(axis=1)+std

			plt.fill_between(values.index.values/60, max_values, min_values, color=p[0].get_color(), alpha=0.15)
	
	plt.ylim([0,1])
	plt.xlim([0,interventions['Time'][vent]/60])
	plt.xticks(fontsize = 18)
	plt.yticks(fontsize = 18)
	plt.ylabel('Fractional Effective Dose', fontsize = 18)
	plt.xlabel('Time (min)', fontsize = 18)
	plt.legend(bbox_to_anchor=(1.01, 0.75), loc='upper left', ncol=1, fontsize = 18)
	plt.subplots_adjust(bottom=0.15, right=0.70)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++ BELOW NOT USED IN REPORT ++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# #------------------------------------------Plot Line Charts for FED-----------------------------------------------


# output_location = '../0_Images/Script_Figures/FED/FED_Line_Gas/'

# if not os.path.exists(output_location):
#     os.makedirs(output_location)

# for vic in victims:

# 	for vent in vent_info:

# 		# Create figure	
# 		fig = plt.figure()
# 		fig.set_size_inches(8, 6)

# 		# Plot style - cycle through 20 color pallet and define markers to cycle through
# 		plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
# 		plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])
	
# 		createplot = False

# 		for exp in vent_info[vent].dropna():
			
# 			if vic == 'Victim_2' and exp == 'Experiment_1_Data':
# 				continue

# 			if vic in FED_Gas[exp]:
# 				createplot = True
# 				plt.plot(FED_Gas[exp][vic], marker = next(plot_markers), markevery=20, label = exp[:-4].replace('_', ' ' ), lw = 2)
# 				if 'Front Door Open' in all_exp_events[exp[:-4]+'Events'].index: 
# 					plt.axvline(all_exp_events[exp[:-4]+'Events']['Time_Seconds']['Front Door Open'], lw = 2, color = 'black')

# 		if createplot == True:
# 			plt.legend()
# 			plt.xlabel('Time (s)')
# 			plt.ylabel('Fractional Effective Dose')
# 			plt.savefig(output_location + vent + '_' + vic + '.pdf')
# 			plt.close('all')

# output_location = '../0_Images/Script_Figures/FED/FED_Line_TempFlux/'

# if not os.path.exists(output_location):
#     os.makedirs(output_location)

# victims = ['Victim_1', 'Victim_2', 'Victim_3', 'Victim_4', 'Victim_5']

# for vic in victims:

# 	for vent in vent_info:
	
# 		# Create figure	
# 		fig = plt.figure()
# 		fig.set_size_inches(8, 6)

# 		# Plot style - cycle through 20 color pallet and define markers to cycle through
# 		plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
# 		plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])
# 		createplot = False

# 		for exp in vent_info[vent].dropna():
			
# 			if vic == 'Victim_2' and exp == 'Experiment_1_Data':
# 				continue

# 			if vic in FED_Temp_Flux[exp]:
# 				createplot = True
# 				plt.plot(FED_Temp_Flux[exp][vic], marker = next(plot_markers), markevery=20, label = exp[:-4].replace('_', ' ' ), lw = 2)
# 				if 'Hall Suppression' in all_exp_events[exp[:-4]+'Events'].index: 
# 					plt.axvline(all_exp_events[exp[:-4]+'Events']['Time_Seconds']['Hall Suppression'], lw = 2, color = 'black')

# 		if createplot == True:
# 			plt.legend()
# 			plt.xlabel('Time (s)')
# 			plt.ylabel('Fractional Effective Dose')
# 			plt.savefig(output_location + vent + '_' + vic + '.pdf')
# 			plt.close('all')

# output_location = '../0_Images/Script_Figures/FED/FED_Line_TempConv/'

# if not os.path.exists(output_location):
#     os.makedirs(output_location)

# victims = ['Victim_1', 'Victim_2', 'Victim_3', 'Victim_4', 'Victim_5']

# for vic in victims:

# 	for vent in vent_info:
	
# 		# Create figure	
# 		fig = plt.figure()
# 		fig.set_size_inches(8, 6)

# 		# Plot style - cycle through 20 color pallet and define markers to cycle through
# 		plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
# 		plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])

# 		createplot = False

# 		for exp in vent_info[vent].dropna():
			
# 			if vic == 'Victim_2' and exp == 'Experiment_1_Data':
# 				continue			

# 			if vic in FED_Temp_Conv[exp]:
# 				createplot = True
# 				plt.plot(FED_Temp_Conv[exp][vic], marker = next(plot_markers), markevery=20, label = exp[:-4].replace('_', ' ' ), lw = 2)
# 				if 'Hall Suppression' in all_exp_events[exp[:-4]+'Events'].index: 
# 					plt.axvline(all_exp_events[exp[:-4]+'Events']['Time_Seconds']['Hall Suppression'], lw = 2, color = 'black')

# 		if createplot == True:
# 			plt.legend()
# 			plt.xlabel('Time (s)')
# 			plt.ylabel('Fractional Effective Dose')
# 			plt.savefig(output_location + vent + '_' + vic + '.pdf')
# 			plt.close('all')

# output_location = '../0_Images/Script_Figures/Additoinal_FED/'

# for exp in ['Experiment_1', 'Experiment_2', 'Experiment_3', 'Experiment_4', 'Experiment_5', 'Experiment_6',
# 			'Experiment_7', 'Experiment_8', 'Experiment_9', 'Experiment_10', 'Experiment_11', 'Experiment_12',
# 			'Experiment_13', 'Experiment_14', 'Experiment_15', 'Experiment_16', 'Experiment_17', 'Experiment_18',
# 			'Experiment_19', 'Experiment_20', 'Experiment_21', 'Experiment_22', 'Experiment_23', 'Experiment_24']:

# 	plt.plot(FED_Temp_Flux[exp + '_Data']['OutSideFR'].index/60,FED_Temp_Flux[exp + '_Data']['OutSideFR'], label='Heat Flux FED')
# 	plt.plot(FED_Temp_Conv[exp + '_Data']['OutSideFR_1'].index/60,FED_Temp_Conv[exp + '_Data']['OutSideFR_1'], label='1ft Temp FED')
# 	plt.plot(FED_Temp_Conv[exp + '_Data']['OutSideFR_3'].index/60,FED_Temp_Conv[exp + '_Data']['OutSideFR_3'], label='3ft Temp FED')
# 	plt.axvline(all_exp_events[exp + '_Events']['Time_Seconds']['Front Door Open']/60, color = 'black')
# 	plt.xlim([0,10])
# 	plt.ylim([0,3])
# 	plt.legend()

# 	if not os.path.exists(output_location):
# 		os.makedirs(output_location)

# 	plt.savefig(output_location + exp + '_FED.png')
# 	plt.close('all')

# output_location = '../0_Images/Script_Figures/Additoinal_FED/Mid_Hall/'

# for exp in ['Experiment_1', 'Experiment_2', 'Experiment_3', 'Experiment_4', 'Experiment_5', 'Experiment_6',
# 			'Experiment_7', 'Experiment_8', 'Experiment_9', 'Experiment_10', 'Experiment_11', 'Experiment_12',
# 			'Experiment_13', 'Experiment_14', 'Experiment_15', 'Experiment_16', 'Experiment_17', 'Experiment_18',
# 			'Experiment_19', 'Experiment_20', 'Experiment_21', 'Experiment_22', 'Experiment_23', 'Experiment_24']:

# 	plt.plot(FED_Temp_Flux[exp + '_Data']['Mid_Hall'].index/60,FED_Temp_Flux[exp + '_Data']['Mid_Hall'], label='FED_Flux MidHall')
# 	plt.plot(FED_Temp_Conv[exp + '_Data']['Mid_Hall'].index/60,FED_Temp_Conv[exp + '_Data']['Mid_Hall'], label='FED_Temp MidHall 1ft')
# 	plt.axvline(all_exp_events[exp + '_Events']['Time_Seconds']['Front Door Open']/60, color = 'black')
# 	plt.xlim([0,10])
# 	plt.ylim([0,3])
# 	plt.legend()

# 	if not os.path.exists(output_location):
# 		os.makedirs(output_location)

# 	plt.savefig(output_location + exp + '_FED.png')
# 	plt.close('all')