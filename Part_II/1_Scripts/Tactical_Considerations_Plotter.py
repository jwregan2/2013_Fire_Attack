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
import matplotlib.transforms as mtransforms
from matplotlib.path import Path
import matplotlib.patches as patches

data_location = '../2_Data/'
info_location = '../3_Info/'
output_location = '../0_Images/Script_Figures/Tactical_Considerations/'

if not os.path.exists(output_location):
	os.makedirs(output_location)

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))

all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))

# print (all_exp_events['Experiment_18_Events'])
# exit()

all_channels = pd.read_csv(info_location + 'Channels.csv').set_index('Channel')
all_gas_channels = pd.read_csv(info_location + 'Gas_Channels.csv').set_index('Channel')

Exp_Des = pd.read_csv(info_location + 'Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

for exp in Exp_Des.index.values:
	channels_to_skip[exp] = Exp_Des['Excluded Channels'][exp].split('|')

# Define 17 color pallet using RGB values - Removed Blue due to water flow potting.
tableau20 = [(255, 127, 14), (255, 187, 120), 
(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Define RGB values in pallet 
for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b / 255.)

print ('-------------------------------------- Plotting Line Charts ----------------------------------')

tactic_consid = {'regrowth':['Experiment_27_Data'], 'expansion':['Experiment_18_Data', 'Experiment_19_Data']} #, 'Experiment_20_Data', 'Experiment_21_Data']}

plots = {'regrowth':{'8TC':['8TC7', '8TC5', '8TC3', '8TC1'],
					 '4TC':['4TC7', '4TC5', '4TC3', '4TC1']},
		 'expansion':{'2BDP':['2BDP5', '2BDP4', '2BDP3', '2BDP2', '2BDP1'],
		 			  '1BDP':['1BDP5', '1BDP4', '1BDP3', '1BDP2', '1BDP1']}}

limits = {'regrowth':[356, 406], 'expansion':[310, 350]}

for tc in tactic_consid.keys():
	
	print ('--------------------------------- ' + tc.replace('_',' ') + ' -----------------------------')
	
	output_location_section = output_location + tc + '/'

	for exp in tactic_consid[tc]:

		print ('Plotting ' + exp[:-5].replace('_',' '))

		for sensor in plots[tc]:
			# if sensor == 'Bedroom_1_Door':
			# 	if not exp == 'Experiment_19_Data':
			# 		continue

			h1 = l1 = h2 = l2 = []

			#Create figure
			fig = plt.figure()

			# plt.style.use('ggplot')

			# Plot style - cycle through 20 color pallet and define markers to cycle through
			plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
			plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

			ax1 = plt.gca()
			ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
			ax1_xlims = ax1.axis()[0:2]
			plt.ylim([0, Exp_Des['Y Scale Temperature'][exp]])
			plt.grid(True)
			plt.xlabel('Time (seconds)', fontsize=48)
			plt.xticks(fontsize=44)
			plt.yticks(fontsize=44)

			axis_scale = Exp_Des['Y Scale Temperature'][exp]

			chart_length = limits[tc][1] - limits[tc][0]

			if chart_length > 50:
				mark = int(chart_length * (4/50))
			else: 
				mark = 4 

			channels = plots[tc][sensor]

			for channel in sorted(channels, reverse=True):
				if channel in channels_to_skip[exp]:
					continue
				if 'BDP' in channel:
					if channel + 'V' in channels_to_skip[exp]:
						continue

				if 'HF' in channel:
					fill_min = 0
					fill_max = float(Exp_Des['Y Scale Wall Heat Flux'][exp])
					y_title = 'Heat Flux (kW/m$^2$)'
				elif 'BDP' in channel:
					if sensor == 'Bedroom_1_Window_Flow':
						fill_min = float(-Exp_Des['Y Scale BDP'][exp]) - 5
						fill_max = float(Exp_Des['Y Scale BDP'][exp]) + 5
					if sensor == 'Bedroom_2_Door':
						fill_min = float(-Exp_Des['Y Scale BDP'][exp]) + 8
						fill_max = float(Exp_Des['Y Scale BDP'][exp]) - 8
					else:
						fill_min = float(-Exp_Des['Y Scale BDP'][exp])
						fill_max = float(Exp_Des['Y Scale BDP'][exp])
					y_title = 'Velocity (m/s)'
				elif 'PT' in channel:
					fill_min = -float(Exp_Des['Y Scale Pressure'][exp])
					fill_max = float(Exp_Des['Y Scale Pressure'][exp])
					y_title = 'Pressure (Pa)'
				elif 'O2' in channel:
					fill_min = 0
					fill_max = 25
					y_title = 'Percent Oxygen'
				else:
					fill_min = 0
					fill_max = float(Exp_Des['Y Scale Temperature'][exp])
					y_title = 'Temperature ($^\circ$F)'

				if 'BDP' in channel:
					channel_name = channel + 'V'
				else:
					channel_name = channel
				
				channel_label = all_channels['Title'][channel_name]

				ax1.plot(all_exp_data[exp][channel].index, all_exp_data[exp][channel], lw = 4, marker=next(plot_markers), markevery=mark,
							label = channel_label, markersize=15)

				if exp in all_flow_data.keys():
					flow_data = all_flow_data[exp]['GPM'] 
					ax1.fill_between(flow_data.index.values, fill_min,  fill_max, where =  flow_data > 10, facecolor='blue', alpha=0.1)

					ax2 = ax1.twinx()
					ax2.plot(all_flow_data[exp].index.values, all_flow_data[exp]['Total Gallons'], lw=6, color='#1f77b4',)
					ax2.set_ylim(0,100)
					ax2.set_ylabel('Total Flow (Gallons)', fontsize=48)
					ax2.tick_params(axis='y', labelsize=44)

			for flow in all_exp_events[exp[:-4]+'Events']['Flow_Time'].dropna().index.values:
				ax1.axvline(all_exp_events[exp[:-4]+'Events']['Flow_Time'][flow], lw=4, color='black')
				ax1.text(all_exp_events[exp[:-4]+'Events']['Flow_Time'][flow], fill_max, flow, ha='left', 
					va='bottom', rotation=45, fontsize=34)

			if exp in all_flow_data.keys():
				h1, l1 = ax1.get_legend_handles_labels()
				h2, l2 = ax2.get_legend_handles_labels()
				ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(-.3, 1.1), loc='lower left', fontsize=40, handlelength=2, labelspacing=.15)
			
			fig.set_size_inches(20, 18) 
			plt.subplots_adjust(top=0.70, left=0.2)

			ax1.set_ylim(fill_min,fill_max)

			ax1.set_ylabel(y_title, fontsize = 48)

			ax1.set_xlim(limits[tc][0],limits[tc][1])

			if tc == 'regrowth':
				ax1.tick_params(axis='x', which='major', pad=15)
				x = linspace(limits[tc][0],limits[tc][1], 6)
				plt.xticks(x, x-366)

			if not os.path.exists(output_location_section +  exp[:-5] + '/'):
				os.makedirs(output_location_section +  exp[:-5] + '/')

			plt.savefig(output_location_section +  exp[:-5] + '/' + sensor +'.pdf')
		plt.close('all')

print ('-------------------------------------- Plotting Steam Expansion Chart ----------------------------------')

#Create figure
fig = plt.figure()

# plt.style.use('ggplot')

# Plot style - cycle through 20 color pallet and define markers to cycle through
plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

ax1 = plt.gca()
ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
ax1_xlims = ax1.axis()[0:2]
plt.ylim([0, Exp_Des['Y Scale Temperature'][exp]])
plt.ylabel('Velocity (m/s', fontsize=48)
plt.grid(True)
plt.xlabel('Time (seconds)', fontsize=48)
plt.xticks(fontsize=44)
plt.yticks(fontsize=44)

window = all_exp_data['Experiment_18_Data'][['1BDP1','1BDP2','1BDP3','1BDP4','1BDP5']]
door = all_exp_data['Experiment_18_Data'][['2BDP1','2BDP2','2BDP3','2BDP4','2BDP5']]


plt.plot(window.mean(axis=1), lw = 4, marker=next(plot_markers), markevery=5, label = 'Avg. Window Velocity', markersize=15)
plt.plot(door.mean(axis=1), lw = 4, marker=next(plot_markers), markevery=5, label = 'Avg. Door Velocity', markersize=15)

plt.ylim([-10,10])
plt.axvline(all_exp_events['Experiment_18_Events']['Flow_Time']['BR1 Window Solid Stream'], lw=4, color='black')
plt.text(all_exp_events['Experiment_18_Events']['Flow_Time']['BR1 Window Solid Stream'],10, 'BR1 Window Solid Stream', ha='left', 
					va='bottom', rotation=45, fontsize=34)

plt.axhline(0, lw=7, color = 'black')

flow_data = all_flow_data['Experiment_18_Data']['GPM'] 
plt.fill_between(flow_data.index.values, -10,  10, where =  flow_data > 10, facecolor='blue', alpha=0.1)

ax2 = ax1.twinx()
ax2.set_ylim(0,2000)
ax2.set_ylabel('Temperature ($^\circ$F)', fontsize=48)
ax2.tick_params(axis='y', labelsize=44)

roomtemp = all_exp_data['Experiment_18_Data'][['1TC1','1TC3','1TC5','1TC7']]
ax2.plot (roomtemp.mean(axis=1), lw = 4, color='green', markevery=5, label = 'Avg. Room Temp', markersize=15)

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc='upper right', fontsize=40, handlelength=2, labelspacing=.15)

plt.xlim([315,350])
plt.subplots_adjust(top=0.70, left=.15, right=0.88)
fig.set_size_inches(20, 18) 
plt.tick_params(axis='x', which='major', pad=20)

if not os.path.exists(output_location +  'Steam_Expansion/'):
	os.makedirs(output_location +  'Steam_Expansion/')

plt.savefig(output_location +  'Steam_Expansion/Experiment_18.pdf')
plt.close('all')

print ('---------- Calculating Flow During Steam Expansion Chart ----------------')

initial = all_flow_data['Experiment_18_Data']['Total Gallons'][all_flow_data['Experiment_18_Data']['Total Gallons'].index>321].iloc[0]
final =  all_flow_data['Experiment_18_Data']['Total Gallons'][all_flow_data['Experiment_18_Data']['Total Gallons'].index>335].iloc[0]

total = final-initial

print ('The total number of Gallons of Water Applied is ' + str(round(total,3)) + ' gallons.')

