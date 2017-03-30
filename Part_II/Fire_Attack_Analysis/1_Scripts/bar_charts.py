import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt
import os

data_location = '../2_Data/FED/'
events_location = '../3_Info/Events/'
output_location = '../0_Images/Results/Script_Figures/FED_Bar'
FED_info = pd.read_csv('../3_Info/Vent_Info.csv')

if not os.path.exists(output_location):
    os.makedirs(output_location)

data_files = ['Intervention_FED.csv', 'Intervention_Plus60_FED.csv', 'Intervention_FED_Temp.csv', 'Intervention_Plus60_FED_Temp.csv']
# data_files = ['Intervention_FED_Temp.csv']

for data_sets in data_files:
	if not os.path.exists(output_location + '/' + data_sets[:-4]):
		os.makedirs(output_location + '/' + data_sets[:-4])
	
	FED_data = pd.read_csv(data_location+data_sets).set_index('index')
	for vent in FED_info:
		if 'Temp' in data_sets:
			vics = ['FED_Temp_Vic1', 'FED_Temp_Vic2', 'FED_Temp_Vic3', 'FED_Temp_Vic4']
			name = 'Temp'
		else:
			vics = ['FED_Vic1', 'FED_Vic2', 'FED_Vic3', 'FED_Vic4']
			name = 'Gas'

		data = pd.DataFrame({'Locations':vics}).set_index('Locations')

		for exp in FED_info[vent].dropna():

			if exp not in FED_data:
				continue
						
			data = pd.concat([data, FED_data[exp]], axis = 1)

			fig, ax = plt.subplots(figsize=(10, 9))
		
		for vic in vics:
			print (vic + '_' + vent)
			vic_data = data.ix[vic].dropna()
			width = 0.5
			plt.bar([p + width for p in list(range(len(vic_data)))],vic_data, width)
			plt.xticks([p + .5 * width for p in list(range(len(vic_data)))], 
				[label.replace('_', ' ') for label in vic_data.index.values.tolist()],rotation = 45)
			plt.savefig(output_location + '/' + data_sets[:-4] + '/' + vent  + '_' + vic + '_' + '.pdf')
			plt.close('all')