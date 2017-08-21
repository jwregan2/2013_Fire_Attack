import os
import pandas as pd
import numpy as np 
import time

event_location = '../3_Info/Events/'

for f in os.listdir(event_location):
	if f.endswith('.csv'):

		if f == 'Experiment_25_Events.csv':
			continue

		data = pd.read_csv(event_location + f)

		if 'Old Time' in data.columns.tolist():
			data = data.drop('Old Time', 1)

		# data['Results_Time'] = np.nan

		# for event in data['Event'].index.values:

		# 	if data['Event'][event] in ['Ignition', 'End Experiment']:
		# 		data.loc[event,'Results_Time'] = data['Time'][event]
		# 	# data['Event'][event] = data['Event'][event].replace('Attack Team', 'Suppression Crew')
		# cols =  data.columns.tolist()
		# vals = [np.nan for c in cols]
		# new_val = dict(zip(cols,vals))
		
		# if f[:-4] not in ['Experiment_' + str(e) + '_Events' for e in [1,12,17]]:
		# 	new_event = 1
		# else:
		# 	new_event = 2

		# new_line = pd.DataFrame(new_val, index = [new_event])

		# data = pd.concat([data.ix[:new_event-1], new_line, data.ix[new_event:]]).reset_index(drop=True)
		# data.loc[new_event,'Results_Time'] = data['Time'][new_event+1]
		# if f[:-4] in ['Experiment_' + str(e) + '_Events' for e in range(1,18)]:
		# 	data.loc[new_event,'Event'] = 'Interior Attack Start'

		# if f[:-4] in ['Experiment_' + str(e) + '_Events' for e in range(18,28)]: 
		if f[:-4] == 'Experiment_27_Events':
			data.loc[1,'Event'] = 'Transitional Attack Start'

		data.to_csv(event_location + f, index=False)
