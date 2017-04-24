import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt
import os
import pickle

data_location = '../2_Data/FED/'
events_location = '../3_Info/Events/'

vent_info = pd.read_csv('../3_Info/Vent_Info.csv')
FED_info = pd.read_csv('../3_Info/FED_info.csv')

all_exp_events = pickle.load(open(events_location+'all_exp_events.dict', 'rb'))

FED_Gas = pickle.load(open(data_location + 'FED_Gas.dict', 'rb'))
FED_Temp_Flux = pickle.load(open(data_location + 'FED_Temp_Flux.dict', 'rb'))
FED_Temp_Conv = pickle.load(open(data_location + 'FED_Temp_Conv.dict', 'rb'))

victims = ['Victim_1', 'Victim_2', 'Victim_3' , 'Victim_4', 'Victim_5']

#-----------------------------------Plot FED Gas by Vent Config-------------------------------
# One chart for all victims. Bar Color the same for victim. 
output_location = '../0_Images/Script_Figures/FED/FED_Bar_Gas/'

victims_gas = victims[:4]

if not os.path.exists(output_location):
    os.makedirs(output_location)

colors = ['m', 'r', 'g' , 'b', 'c']

for vent in vent_info:
	
	plt_length = pd.DataFrame({'Victim':victims_gas}).set_index('Victim')
	for exp in vent_info[vent].dropna():
		plt_length[exp] = np.zeros(len(victims_gas))
		for victim in victims_gas:
			if victim in FED_Gas[exp]:
				plt_length[exp][victim] = 1

	print (plt_length)
	exit()	

	pos = pd.DataFrame({'Victim':victims_gas, 'Pos':[l/4 for l in plt_length]}).set_index('Victim')
	print (pos)
	exit()

	width = .25
	
	for exp in vent_info[vent].dropna():
		
		for vic in victims_gas:
			if vic not in FED_Gas[exp]:
				pos['Pos'][vic] = pos['Pos'][vic] - width
				continue

			if vic == 'Victim_2' and exp == 'Experiment_1_Data':
				continue

			first_event = int(all_exp_events[exp[:-4]+'Events']['Time_Seconds'][1])
			
			if exp == vent_info[vent][1]:
				plt.bar(((int(vic[-1])-1)*2)+pos['Pos'][vic], FED_Gas[exp][vic][first_event], width, color = colors[int(vic[-1])-1], label = vic.replace('_', ' '))
			else:
				plt.bar(((int(vic[-1])-1)*2)+pos['Pos'][vic], FED_Gas[exp][vic][first_event], width, color = colors[int(vic[-1])-1])
		
		pos['Pos'] = pos['Pos'] + width
	
	# plt.title(vent.replace('_',' '))
	plt.ylim([0,1])
	plt.ylabel('Fractional Effective Dose')
	plt.legend(bbox_to_anchor=(1.05, 0.75), loc='upper left', ncol=1)
	plt.xticks(np.arange(len(victims_gas))*2+0.75, [vic.replace('_', ' ') for vic in victims_gas], rotation = 45)
	plt.subplots_adjust(bottom=0.15, right=0.75)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

exit()
#-----------------------------------Plot FED Temp Conv by Vent Config-------------------------------
# One chart for all victims. Bar Color the same for victim. 
output_location = '../0_Images/Script_Figures/FED/FED_Bar_TempConv/'

victims_temp = victims

if not os.path.exists(output_location):
    os.makedirs(output_location)

colors = ['m', 'r', 'g' , 'b', 'c']


for vent in vent_info:
	
	pos = 0

	for exp in vent_info[vent].dropna():
		
		for vic in victims_temp:
			if vic not in FED_Temp_Conv[exp]:
				continue

			first_event = int(all_exp_events[exp[:-4]+'Events']['Time_Seconds'][1])
			
			width = .25

			if exp == vent_info[vent][1]:
				plt.bar(((int(vic[-1])-1)*2)+pos, FED_Temp_Conv[exp][vic][first_event], width, color = colors[int(vic[-1])-1], label = vic.replace('_', ' '))
			else:
				plt.bar(((int(vic[-1])-1)*2)+pos, FED_Temp_Conv[exp][vic][first_event], width, color = colors[int(vic[-1])-1])
		
		pos = pos + .25
	
	# plt.title(vent.replace('_',' '))
	plt.ylim([0,1])
	plt.ylabel('Fractional Effective Dose')
	plt.legend(bbox_to_anchor=(1.05, 0.75), loc='upper left', ncol=1)
	plt.xticks(np.arange(len(victims_gas))*2+0.75, [vic.replace('_', ' ') for vic in victims_gas], rotation = 45)
	plt.subplots_adjust(bottom=0.15, right=0.75)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

#-----------------------------------Plot FED Temp Flux by Vent Config-------------------------------
# One chart for all victims. Bar Color the same for victim. 
output_location = '../0_Images/Script_Figures/FED/FED_Bar_TempFlux/'

victims_temp = victims

if not os.path.exists(output_location):
    os.makedirs(output_location)

colors = ['m', 'r', 'g' , 'b', 'c']


for vent in vent_info:
	
	pos = pd.DataFrame('victims_temp')

	width = 2/len(FED_info[vent].dropna())

	for exp in vent_info[vent].dropna():
		
		for vic in victims_temp:
			if vic not in FED_Temp_Flux[exp]:
				
				continue

			first_event = int(all_exp_events[exp[:-4]+'Events']['Time_Seconds'][1])

			if exp == vent_info[vent][1]:
				plt.bar(((int(vic[-1])-1)*2)+pos, FED_Temp_Flux[exp][vic][first_event], width, color = colors[int(vic[-1])-1], label = vic.replace('_', ' '))
			else:
				plt.bar(((int(vic[-1])-1)*2)+pos, FED_Temp_Flux[exp][vic][first_event], width, color = colors[int(vic[-1])-1])
		
		pos = pos + width
	
	plt.ylim([0,1])
	plt.ylabel('Fractional Effective Dose')
	plt.legend(bbox_to_anchor=(1.05, 0.75), loc='upper left', ncol=1)
	plt.xticks(np.arange(len(victims_gas))*2+0.75, [vic.replace('_', ' ') for vic in victims_gas], rotation = 45)
	plt.subplots_adjust(bottom=0.15, right=0.75)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

#-----------------------------------Plot FED Gas 60 sec post suppression by Vent Config-------------------------------
# One chart for all victims. Bar Color the same for victim. 
output_location = '../0_Images/Script_Figures/FED/FED_Bar_Gas_Intervention/'

victims_gas = victims[:4]

if not os.path.exists(output_location):
    os.makedirs(output_location)

colors = ['m', 'r', 'g' , 'b', 'c']


for vent in FED_info:
	
	pos = 0
	width = 2/len(FED_info[vent].dropna())

	for exp in FED_info[vent].dropna():
		
		for vic in victims_gas:
			if vic not in FED_Gas[exp]:
				continue

			first_event = int(all_exp_events[exp[:-4]+'Events']['Time_Seconds'][1])
			
			#Calculate FED increase after first intervention
			value = FED_Gas[exp][vic][first_event+60] - FED_Gas[exp][vic][first_event]

			# If first bar from victim plot with label
			if exp == vent_info[vent][1]:
				plt.bar(((int(vic[-1])-1)*2)+pos, value, width, color = colors[int(vic[-1])-1], label = vic.replace('_', ' '))
			else:
				plt.bar(((int(vic[-1])-1)*2)+pos, value, width, color = colors[int(vic[-1])-1])
		
		pos = pos + width
	
	# plt.title(vent.replace('_',' '))
	plt.ylim([0,1])
	plt.ylabel('Fractional Effective Dose')
	plt.legend(bbox_to_anchor=(1.05, 0.75), loc='upper left', ncol=1)
	plt.xticks(np.arange(len(victims_gas))*2+0.75, [vic.replace('_', ' ') for vic in victims_gas], rotation = 45)
	plt.subplots_adjust(bottom=0.15, right=0.75)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

#-----------------------------------Plot FED Temp Conv 60 sec post suppression by Vent Config-------------------------------
# One chart for all victims. Bar Color the same for victim. 
output_location = '../0_Images/Script_Figures/FED/FED_Bar_TempConv_Intervention/'

victims_temp = victims

if not os.path.exists(output_location):
    os.makedirs(output_location)

colors = ['m', 'r', 'g' , 'b', 'c']


for vent in FED_info:
	
	pos = 0
	width = 2/len(FED_info[vent].dropna())
	
	for exp in FED_info[vent].dropna():
		
		for vic in victims_temp:
			if vic not in FED_Temp_Conv[exp]:
				continue

			first_event = int(all_exp_events[exp[:-4]+'Events']['Time_Seconds'][1])
			
			value = FED_Temp_Conv[exp][vic][first_event + 60] - FED_Temp_Conv[exp][vic][first_event]

			if exp == vent_info[vent][1]:
				plt.bar(((int(vic[-1])-1)*2)+pos, value, width, color = colors[int(vic[-1])-1], label = vic.replace('_', ' '))
			else:
				plt.bar(((int(vic[-1])-1)*2)+pos, value, width, color = colors[int(vic[-1])-1])
		
		pos = pos + width
	
	plt.ylim([0,1])
	plt.ylabel('Fractional Effective Dose')
	plt.legend(bbox_to_anchor=(1.05, 0.75), loc='upper left', ncol=1)
	plt.xticks(np.arange(len(victims_gas))*2+0.75, [vic.replace('_', ' ') for vic in victims_gas], rotation = 45)
	plt.subplots_adjust(bottom=0.15, right=0.75)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')

#-----------------------------------Plot FED Temp Flux 60 sec post suppression by Vent Config-------------------------------
# One chart for all victims. Bar Color the same for victim. 
output_location = '../0_Images/Script_Figures/FED/FED_Bar_TempFlux_Intervention/'

victims_temp = victims

if not os.path.exists(output_location):
    os.makedirs(output_location)

colors = ['m', 'r', 'g' , 'b', 'c']


for vent in FED_info:
	
	pos = 0
	width = 2/len(FED_info[vent].dropna())

	for exp in FED_info[vent].dropna():

		for vic in victims_temp:
			if vic not in FED_Temp_Flux[exp]:
				continue

			first_event = int(all_exp_events[exp[:-4]+'Events']['Time_Seconds'][1])
			
			value = FED_Temp_Flux[exp][vic][first_event + 60] - FED_Temp_Flux[exp][vic][first_event]

			if exp == vent_info[vent][1]:
				plt.bar(((int(vic[-1])-1)*2)+pos, value, width, color = colors[int(vic[-1])-1], label = vic.replace('_', ' '))
			else:
				plt.bar(((int(vic[-1])-1)*2)+pos, value, width, color = colors[int(vic[-1])-1])
		
		pos = pos + width
	
	plt.ylim([0,1])
	plt.ylabel('Fractional Effective Dose')
	plt.legend(bbox_to_anchor=(1.05, 0.75), loc='upper left', ncol=1)
	plt.xticks(np.arange(len(victims_gas))*2+0.75, [vic.replace('_', ' ') for vic in victims_gas], rotation = 45)
	plt.subplots_adjust(bottom=0.15, right=0.75)
	plt.savefig(output_location + vent + '.pdf')
	plt.close('all')


