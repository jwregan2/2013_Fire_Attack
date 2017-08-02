# Get times of all water flows for experiments and match them to the flows from the events file.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import pickle
from itertools import cycle
import os as os
from pylab import * 
import datetime

data_location = '../2_Data/'
info_location = '../3_Info/'
output_location = '../3_Info/Flow_Times/'

if not os.path.exists(output_location):
	os.makedirs(output_location)

flow_times = {} 

# Load flow data from dictionary
all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))
all_event_data = pickle.load(open(info_location + 'Events/all_exp_events.dict', 'rb'))

print (all_event_data['Experiment_6_Events'])
exit()

for exp in list(all_flow_data.keys()):
	print(exp)
	
	flow_times[exp] = pd.DataFrame(columns=['Time'])

	started_flow = False

	for val in all_flow_data[exp].index.values:
		
		# if exp == 'Experiment_21_Data':
		# 	plt.plot(all_flow_data[exp]['GPM'])
		# 	plt.show()
		# 	exit()

		if int(all_flow_data[exp]['GPM'][val]) < 10:
			started_flow = False

		if started_flow == True:
			continue

		if all_flow_data[exp]['GPM'][val] > 10:
			flow_times[exp] = flow_times[exp].append(pd.DataFrame([val], columns=['Time']), ignore_index=True)
			started_flow = True
		else:
			started_flow = False

	flow_times[exp].to_csv(output_location + exp + '.csv')

plt.plot(all_flow_data['Experiment_24_Data']['GPM'])
plt.show()

