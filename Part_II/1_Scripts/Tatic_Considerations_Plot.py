import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt 
import pickle
from itertools import cycle
import os as os
from pylab import * 
import datetime
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle
import matplotlib.transforms as mtransforms

data_location = '../2_Data/'
info_location = '../3_Info/'
output_location = '../0_Images/Script_Figures/Tactical_Considerations/Flow_vs_Shutdown/'

if not os.path.exists(output_location):
	os.makedirs(output_location)

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))

all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))

all_channels = pd.read_csv(info_location + 'Channels.csv').set_index('Channel')

Exp_Des = pd.read_csv(info_location + 'Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

for exp in Exp_Des.index.values:
	channels_to_skip[exp] = Exp_Des['Excluded Channels'][exp].split('|')

print ('---------------------------------Plot Flow & Move vs. Shutdown and Move -----------------------------') 

experiments = {'No':['Experiment_2_Data', 'Experiment_6_Data'], 'Single':['Experiment_7_Data', 'Experiment_8_Data'], 'Two':['Experiment_13_Data','Experiment_14_Data']}

experiment = ['Experiment_2_Data', 'Experiment_6_Data','Experiment_7_Data', 'Experiment_8_Data', 'Experiment_13_Data','Experiment_14_Data']

channels = {'End_Hall':['3TC7','3TC6','3TC5','3TC4','3TC3','3TC2','3TC1'], 
			'Mid_Hall':['4TC1','4TC2','4TC3','4TC4','4TC5','4TC6','4TC7'],
			'Start_Hall':['5TC1','5TC2','5TC3','5TC4','5TC5','5TC6','5TC7'],
			'Living_Room':['6TC1','6TC2','6TC3','6TC4','6TC5','6TC6','6TC7'],
			'Bedroom_3':['8TC1','8TC3','8TC5','8TC7'],
			'Bedroom_1':['1TC1', '1TC3', '1TC5', '1TC7'],
			'Bedroom_2':['2TC1','2TC3','2TC5', '2TC7']}

# experiment = all_exp_data.keys()

# channels = {'Bedroom_1':['1TC1', '1TC3', '1TC5', '1TC7']}

for exp in experiment:
	print ('Plotting ' + exp[:-5].replace('_',' '))
	for sensor in channels:

		if exp not in all_flow_data.keys():
			continue

# for vent in experiments:

		#Create figure
		fig = plt.figure()
		
		plt.style.use('ggplot')

		# Define 20 color pallet using RGB values
		tableau20 = [(255, 127, 14), (255, 187, 120), 
		(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
		(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
		(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
		(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

		# Define RGB values in pallet 
		for i in range(len(tableau20)):
				r, g, b = tableau20[i]
				tableau20[i] = (r / 255., g / 255., b / 255.)

		# Plot style - cycle through 20 color pallet and define markers to cycle through
		plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
		plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

		ax1 = plt.gca()
		ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
		ax1_xlims = ax1.axis()[0:2]
		plt.ylim([0, Exp_Des['Y Scale Temperature'][exp]])
		plt.grid(True)
		plt.xlabel('Time (min)', fontsize=32)
		plt.xticks(fontsize=28)
		plt.yticks(fontsize=28)
		plt.ylabel('Temperature ($^\circ$F)', fontsize = 32)

		ax2 = ax1.twinx()
		ax2.plot(all_flow_data[exp].index.values/60, all_flow_data[exp]['Total Gallons'], lw=4, color='#1f77b4',)
		ax2.set_ylim(0,350)
		ax2.set_ylabel('Total Flow (Gallons)', fontsize=32)
		ax2.tick_params(axis='y', labelsize=28)

		axis_scale = Exp_Des['Y Scale Temperature'][exp]

		if Exp_Des['Speed'][exp] == 'high':
			mark = 100
		if Exp_Des['Speed'][exp] == 'low':
			mark = 5

		for channel in sorted(channels[sensor], reverse=True):
			if channel in channels_to_skip[exp]:
				continue
			ax1.plot(all_exp_data[exp][channel].index/60, all_exp_data[exp][channel], lw = 2, marker=next(plot_markers), markevery=mark,
						label = all_channels['Title'][channel])
		
		flow_data = all_flow_data[exp]['GPM'] 

		if 'HF' in channel:
			fill = 5
		else:
			fill = Exp_Des['Y Scale Temperature'][exp]	
		
		if 'Burst Suppression' in all_exp_events[exp[:-4]+ 'Events'].index.values:
			ax1.axvline(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Burst Suppression']/60, lw = 2, color='black')
		
		if 'Hall Suppression' in all_exp_events[exp[:-4]+ 'Events'].index.values:
			ax1.axvline(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Hall Suppression']/60, lw = 2, color='black')

		ax1.fill_between(flow_data.index.values/60, 0,  fill, where =  flow_data > 10, facecolor='blue', alpha=0.3)

		plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60, 
		# plt.xlim([0, 
					all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['End Experiment']/60])
		fig.set_size_inches(20, 16)
		
		h1, l1 = ax1.get_legend_handles_labels()
		h2, l2 = ax2.get_legend_handles_labels()
		ax1.legend(h1+h2, l1+l2, loc='upper right', fontsize=24, handlelength=3)

		if not os.path.exists(output_location +  exp[:-5] + '/'):
			os.makedirs(output_location +  exp[:-5] + '/')

		plt.savefig(output_location +  exp[:-5] + '/' + sensor +'.pdf')
		plt.close('all')
