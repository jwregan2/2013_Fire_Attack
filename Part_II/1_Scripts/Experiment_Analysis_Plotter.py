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
output_location = '../0_Images/Script_Figures/Experiment_Analysis/'

if not os.path.exists(output_location):
	os.makedirs(output_location)

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))

all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))

all_channels = pd.read_csv(info_location + 'Channels.csv').set_index('Channel')

Exp_Des = pd.read_csv(info_location + 'Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

print ('-------------------------------------- Plotting Line Charts ----------------------------------')

for exp in Exp_Des.index.values:
	channels_to_skip[exp] = Exp_Des['Excluded Channels'][exp].split('|')

experiment = {'Flow_vs_Shutdown':['Experiment_3_Data', 'Experiment_2_Data', 'Experiment_6_Data','Experiment_7_Data', 'Experiment_8_Data', 'Experiment_9_Data', 'Experiment_10_Data', 'Experiment_13_Data','Experiment_14_Data'],
			'Pushing_Fire':['Experiment_7_Data','Experiment_8_Data','Experiment_9_Data','Experiment_10_Data','Experiment_11_Data','Experiment_18_Data','Experiment_19_Data','Experiment_20_Data','Experiment_21_Data']}

channels = {'Flow_vs_Shutdown':{'End_Hall':['3TC7','3TC6','3TC5','3TC4','3TC3','3TC2','3TC1'], 
							'Bedroom_1':['1TC1', '1TC3', '1TC5', '1TC7'],
							'Start_Hall_Flow':['6BDP1','6BDP2','6BDP3','6BDP4','6BDP5']},
			'Pushing_Fire':{'Start_Hall_Flow':['6BDP1','6BDP2','6BDP3','6BDP4','6BDP5'],
							'Bedroom_1_Window_Flow':['1BDP1','1BDP2','1BDP3','1BDP4','1BDP5']}
			}

for section in experiment.keys():
	
	print ('--------------------------------- ' + section.replace('_',' ') + ' -----------------------------')
	
	output_location_section = output_location + section + '/'

	for exp in experiment[section]:

		print ('Plotting ' + exp[:-5].replace('_',' '))

		for sensor in channels[section]:
			h1 = l1 = h1 = l2 = []

			#Create figure
			fig = plt.figure()
			
			# plt.style.use('ggplot')

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
			plt.xlabel('Time (min)', fontsize=48)
			plt.xticks(fontsize=44)
			plt.yticks(fontsize=44)

			if exp in all_flow_data.keys():
				ax2 = ax1.twinx()
				ax2.plot(all_flow_data[exp].index.values/60, all_flow_data[exp]['Total Gallons'], lw=6, color='#1f77b4',)
				ax2.set_ylim(0,400)
				ax2.set_ylabel('Total Flow (Gallons)', fontsize=48)
				ax2.tick_params(axis='y', labelsize=44)

			axis_scale = Exp_Des['Y Scale Temperature'][exp]

			if Exp_Des['Speed'][exp] == 'high':
				mark = 100
			if Exp_Des['Speed'][exp] == 'low':
				mark = 5

			for channel in sorted(channels[section][sensor], reverse=True):
				if channel in channels_to_skip[exp]:
					continue
				if 'BDP' in channel:
					if channel + 'V' in channels_to_skip[exp]:
						continue

				if 'HF' in channel:
					fill_min = 0
					fill_max = float(Exp_Des['Y Scale HF'][exp])
					y_title = 'Heat Flux (kW/m$^2$'
				elif 'BDP' in channel:
					if sensor == 'Bedroom_1_Window_Flow':
						fill_min = float(-Exp_Des['Y Scale BDP'][exp]) - 5
						fill_max = float(Exp_Des['Y Scale BDP'][exp]) + 5
					else:
						fill_min = float(-Exp_Des['Y Scale BDP'][exp])
						fill_max = float(Exp_Des['Y Scale BDP'][exp])
					y_title = 'Velocity (m/s)'
				else:
					fill_min = 0
					fill_max = float(Exp_Des['Y Scale Temperature'][exp])
					y_title = 'Temperature ($^\circ$F)'	

				if 'BDP' in channel:
					channel_name = channel + 'V'
				else:
					channel_name = channel
 
				ax1.plot(all_exp_data[exp][channel].index/60, all_exp_data[exp][channel], lw = 4, marker=next(plot_markers), markevery=mark,
							label = all_channels['Title'][channel_name])

				if exp in all_flow_data.keys():
					flow_data = all_flow_data[exp]['GPM'] 
					ax1.fill_between(flow_data.index.values/60, fill_min,  fill_max, where =  flow_data > 10, facecolor='blue', alpha=0.1)

			if 'Burst Suppression' in all_exp_events[exp[:-4]+ 'Events'].index.values:
				if exp in ['Experiment_8_Data', 'Experiment_14_Data']:
					burst = -0.1
				else:
					burst = 0
				ax1.axvline(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Burst Suppression']/60, lw = 4, color='black')
				ax1.text(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Burst Suppression']/60+burst, fill_max, 'Burst Suppression',
					ha='left', va='bottom', rotation=45, fontsize=34)
			
			if 'Hall Suppression' in all_exp_events[exp[:-4]+ 'Events'].index.values:
				ax1.axvline(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Hall Suppression']/60, lw = 4, color='black')
				ax1.text(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Hall Suppression']/60, fill_max, 'Hall Suppression', 
					ha='left', va='bottom', rotation=45, fontsize=34)

			if exp in all_flow_data.keys():
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60, 
				# plt.xlim([0, 
							# all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['End Experiment']/60])
							np.minimum(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['End Experiment']/60, np.max(all_flow_data[exp].index.values)/60)])
			else:
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60, 
							10.5])

			if exp == 'Experiment_14_Data':
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60,12])
			if exp == 'Experiment_17_Data':
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60,10])
			
			fig.set_size_inches(20, 18)
			
			
			if exp in all_flow_data.keys():
				h1, l1 = ax1.get_legend_handles_labels()
				h2, l2 = ax2.get_legend_handles_labels()
				ax1.legend(h1+h2, l1+l2, loc='upper right', fontsize=40, handlelength=3, labelspacing=.15)

			ax1.set_ylim(fill_min,fill_max)
			ax1.set_ylabel(y_title, fontsize = 48)
			
			plt.subplots_adjust(top=0.8)

			if section == 'Flow_vs_Shutdown':
				if exp in ['Experiment_1_Data', 'Experiment_12_Data', 'Experiment_17_Data']:
					ax1.set_ylim([fill_min*1.25, fill_max*1.25])
					ax1.legend(loc='upper right', fontsize=40, handlelength=3, labelspacing=.15)
					plt.subplots_adjust(top=.9)

			if not os.path.exists(output_location_section +  exp[:-5] + '/'):
				os.makedirs(output_location_section +  exp[:-5] + '/')

			
			plt.savefig(output_location_section +  exp[:-5] + '/' + sensor +'.pdf')
		plt.close('all')

print ('---------------------------------Plotting Heatflux & Temperature Plot -----------------------------')

experiments = ['Experiment_1_Data', 'Experiment_12_Data', 'Experiment_14_Data']

channels = pd.DataFrame({'Temp':['3TC1','3TC3','3TC5','4TC1','5TC1'], 'Heat_Flux':['1HF1','1HF3','1HF5','2HF','3HF']})

plot_data = {}

for exp in experiments:
	data_temp = []
	data_HF = []
	for chan in channels.index:

		data_temp.append(all_exp_data[exp][channels['Temp'][chan]][362:392].mean())
		data_HF.append(all_exp_data[exp][channels['Heat_Flux'][chan]][362:392].mean())

	plot_data[exp] = list(zip(data_temp,data_HF))

fig = plt.figure()
ax = plt.gca()

ax.set_xlabel('Heat Flux (kW/m$^2$)',fontsize=16)
ax.set_ylabel('Temperature ($^{\circ}$C)',fontsize=16)
ax.set_axisbelow(True)
plt.grid(linestyle='-',linewidth = 1.5)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim([.1,200])
ax.set_ylim([10,1000])
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
for axis in [ax.xaxis, ax.yaxis]:
		 axis.set_major_formatter(ScalarFormatter())

plt.fill_between([1,2],[20,20],[70,70], color = 'g',edgecolor='black',alpha=0.85)
plt.text(1.4, 37,'R\nO\nU\nT\nI\nN\nE', va='center', ha='center', color='white', fontsize=18, linespacing=.8)

plt.fill_between([2,12],[70,70],[200,200], color = 'y',edgecolor='black',alpha=0.85)
plt.text(4.75, 115, 'ORDINARY', va='center', ha='center', color='white', fontsize=16)


plt.fill_between([12,200],[200,200],[1200,1200], color = 'r',edgecolor='black',alpha=0.86)
plt.text(50, 430, 'EMERGENCY', va='center', ha='center', color='white', fontsize=16)

for exp in plot_data.keys():
	for location in plot_data[exp]:
		plt.plot(location, marker='x')

fig.set_size_inches(10, 7)
plt.tight_layout()	

if not os.path.exists(output_location + '/Thermal_Class/'):
	os.makedirs(output_location + '/Thermal_Class/')

plt.savefig(output_location + '/Thermal_Class/' + 'Test.pdf')

# plt.close('all')

