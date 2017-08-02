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
output_location = '../0_Images/Script_Figures/Experiment_Analysis/'

if not os.path.exists(output_location):
	os.makedirs(output_location)

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))

all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))

# print (all_exp_events['Experiment_3_Events'])

# plt.plot(all_flow_data['Experiment_3_Data']['GPM'])
# plt.axvline(512.0, lw=1)
# plt.axvline(524.4, lw=1)
# plt.show()
# exit()

all_channels = pd.read_csv(info_location + 'Channels.csv').set_index('Channel')

Exp_Des = pd.read_csv(info_location + 'Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

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

for exp in Exp_Des.index.values:
	channels_to_skip[exp] = Exp_Des['Excluded Channels'][exp].split('|')

experiment = {'Flow_vs_Shutdown':['Experiment_3_Data', 'Experiment_2_Data', 'Experiment_6_Data','Experiment_7_Data', 'Experiment_8_Data', 'Experiment_9_Data', 'Experiment_10_Data', 'Experiment_13_Data','Experiment_14_Data'],
			'Pushing_Fire':['Experiment_7_Data','Experiment_8_Data','Experiment_9_Data','Experiment_10_Data','Experiment_11_Data','Experiment_18_Data','Experiment_19_Data','Experiment_20_Data','Experiment_21_Data'],
			'Door_Control':['Experiment_3_Data', 'Experiment_6_Data', 'Experiment_14_Data', 'Experiment_15_Data']}

channels = {'Flow_vs_Shutdown':{'End_Hall':['3TC7','3TC6','3TC5','3TC4','3TC3','3TC2','3TC1'], 
							'Bedroom_1_Temperature':['1TC1', '1TC3', '1TC5', '1TC7'],
							'Start_Hall_Flow':['6BDP1','6BDP2','6BDP3','6BDP4','6BDP5']},
			'Pushing_Fire':{'Start_Hall_Flow':['6BDP1','6BDP2','6BDP3','6BDP4','6BDP5'],
							'Bedroom_1_Window_Flow':['1BDP1','1BDP2','1BDP3','1BDP4','1BDP5'],
							'Front_Door_Flow':['7BDP1','7BDP2','7BDP3','7BDP4','7BDP5'],
							'Bedroom_1_Door':['2BDP1','2BDP2','2BDP3','2BDP4','2BDP5'],
							'Bedroom_2_Door':['3BDP1','3BDP2','3BDP3','3BDP4','3BDP5'],
							'Bedroom_3_Door':['5BDP1','5BDP2','5BDP3','5BDP4','5BDP5']},
			'Door_Control':{'Bedroom_1_Temperature':['1TC1', '1TC3', '1TC5', '1TC7'],
							'Start_Hall_Flow':['6BDP1','6BDP2','6BDP3','6BDP4','6BDP5'],
							'Hall_Heat_Flux':['1HF1','1HF3','1HF5'],
							'Start_Hall_Temp':['5TC7','5TC6','5TC5','5TC4','5TC3','5TC2','5TC1']}}

interior = ['Experiment_1_Data', 'Experiment_2_Data', 'Experiment_3_Data','Experiment_4_Data', 'Experiment_5_Data', 
			'Experiment_6_Data', 'Experiment_7_Data', 'Experiment_8_Data','Experiment_9_Data', 'Experiment_10_Data',
			'Experiment_11_Data', 'Experiment_12_Data', 'Experiment_13_Data','Experiment_14_Data', 'Experiment_15_Data',
			'Experiment_16_Data', 'Experiment_17_Data']

exterior = ['Experiment_18_Data', 'Experiment_19_Data', 'Experiment_20_Data','Experiment_21_Data', 'Experiment_22_Data', 
			'Experiment_23_Data', 'Experiment_24_Data', 'Experiment_27_Data']

for section in experiment.keys():
	
	print ('--------------------------------- ' + section.replace('_',' ') + ' -----------------------------')
	
	output_location_section = output_location + section + '/'

	for exp in experiment[section]:

		print ('Plotting ' + exp[:-5].replace('_',' '))

		for sensor in channels[section]:
			# if sensor == 'Bedroom_1_Door':
			# 	if not exp == 'Experiment_19_Data':
			# 		continue

			h1 = l1 = h1 = l2 = []

			#Create figure
			fig = plt.figure()
			fig.set_size_inches(8, 6)

			# plt.style.use('ggplot')

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

				if sensor == 'Bedroom_1_Window_Flow' or sensor == 'Bedroom_1_Door' or sensor == 'Bedroom_2_Door':
					channel_label = 'Bed' + all_channels['Title'][channel_name][7:]
					if channel_label[-6:] == 'Middle':
						if channel_label == 'Middle':
							continue
						else:
							channel_label = channel_label.replace('Middle', 'Mid.')
				else:
					channel_label = all_channels['Title'][channel_name]

				ax1.plot(all_exp_data[exp][channel].index/60, all_exp_data[exp][channel], lw = 4, marker=next(plot_markers), markevery=mark,
							label = channel_label)

				if exp in all_flow_data.keys():
					flow_data = all_flow_data[exp]['GPM'] 
					ax1.fill_between(flow_data.index.values/60, fill_min,  fill_max, where =  flow_data > 10, facecolor='blue', alpha=0.1)

			# Plot flow markers for initial water flow for both intereior and exterior fire attacks.
			if exp in interior:
				for flow in ['Burst Suppression', 'Hall Suppression']:
					if flow not in all_exp_events[exp[:-4]+'Events']['Flow_Time'].dropna().index.values:
						continue
					ax1.axvline(all_exp_events[exp[:-4]+'Events']['Flow_Time'][flow]/60, lw=4, color='black')
					ax1.text(all_exp_events[exp[:-4]+'Events']['Flow_Time'][flow]/60, fill_max, flow, ha='left', 
						va='bottom', rotation=45, fontsize=34)

			
			if exp in exterior:
				for flow in ['BR1 Window Suppression','BR1 Window Solid Stream','BR1 Window Narrow Fog', 
							'BR1 Window Straight Stream','BR1 Window Solid Stream', 'BR2 Window Straight Stream',
							'BR4 Window Straight Stream']:
					if flow not in all_exp_events[exp[:-4]+'Events']['Flow_Time'].dropna().index.values:
						continue
					ax1.axvline(all_exp_events[exp[:-4]+'Events']['Flow_Time'][flow]/60, lw=4, color='black')
					ax1.text(all_exp_events[exp[:-4]+'Events']['Flow_Time'][flow]/60, fill_max, flow, ha='left', 
						va='bottom', rotation=45, fontsize=34)

			# Plot front door open for experiments where door was opened
			if exp not in ['Experiment_18_Data', 'Experiment_19_Data', 'Experiment_20_Data']:
				if 'Front Door Open' in all_exp_events[exp[:-4]+ 'Events'].index.values:
					ax1.axvline(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Front Door Open']/60, lw = 4, color='black')
					ax1.text(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['Front Door Open']/60, fill_max, 'Front Door Open', 
						ha='left', va='bottom', rotation=45, fontsize=34)

			if section == 'Door_Control':
				if exp == 'Experiment_3_Data':
					ax1.axvline(521/60, lw=4, color = 'black')
					ax1.text(519/60, fill_max, 'Door Controlled', ha='left', va='bottom', rotation=45, fontsize=34)
				if exp == 'Experiment_15_Data':
					ax1.axvline(351/60, lw=4, color = 'black')
					ax1.text(351/60, fill_max, 'Door Controlled', ha='left', va='bottom', rotation=45, fontsize=34)

			if exp in all_flow_data.keys():
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60, 
				# plt.xlim([0, 
							# all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['End Experiment']/60])
							np.minimum(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['End Experiment']/60, np.max(all_flow_data[exp].index.values)/60)])
			else:
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60, 
							10.5])

			#For Experiment 14 & 17 Adjust the end chart time.
			if exp == 'Experiment_14_Data':
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60,12])
			if exp == 'Experiment_17_Data':
				plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60,10])

			if section == 'Door_Control':
				if exp == 'Experiment_6_Data':
					plt.xlim([(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]-15)/60, 
						(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]+105)/60])
				else:
					plt.xlim([(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]-15)/60, 
						(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]+90)/60])

			
			#For Exterior Attacks Set the graph to start 60 seconds before attack. 
			if exp in ['Experiment_18_Data', 'Experiment_19_Data', 'Experiment_20_Data', 'Experiment_21_Data']:
				plt.xlim([(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]-60)/60,
					np.minimum(all_exp_events[exp[:-4] + 'Events']['Time_Seconds']['End Experiment']/60, np.max(all_flow_data[exp].index.values)/60)])
						
			#For Pushing Fire Set chart to end 60 seconds after suppression
			if section == 'Pushing_Fire':
				if exp in ['Experiment_18_Data', 'Experiment_19_Data', 'Experiment_20_Data']:
					plt.xlim([(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]-15)/60,
						(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]+90)/60])
				else:
					plt.xlim([all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]/60,
						(all_exp_events[exp[:-4] + 'Events']['Time_Seconds'][1]+90)/60])

			if exp in ['Experiment_18_Data', 'Experiment_19_Data', 'Experiment_20_Data', 'Experiment_21_Data']:
				plt.subplots_adjust(top=0.70, right = 0.85)
				if exp == 'Experiment_19_Data':
					plt.subplots_adjust(top=0.70, right = 0.85)
			elif section == 'Door_Control':
				plt.subplots_adjust(top=0.70, right = 0.85)
			else:
				plt.subplots_adjust(top=0.70)

			fig.set_size_inches(20, 18)
			
			if exp in all_flow_data.keys():
				h1, l1 = ax1.get_legend_handles_labels()
				h2, l2 = ax2.get_legend_handles_labels()
				if section == 'Pushing_Fire':
					if exp in ['Experiment_18_Data', 'Experiment_19_Data', 'Experiment_20_Data', 'Experiment_21_Data']:
						ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(1.2, 1.03), loc='lower right', fontsize=40, handlelength=2, labelspacing=.15)
						if exp == 'Experiment_19_Data':
							ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(1.2, 1.03), loc='lower right', fontsize=40, handlelength=1.5, labelspacing=.15)
					else:
						ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(1.13, 1.03), loc='lower right', fontsize=40, handlelength=2, labelspacing=.15)
				elif section == 'Door_Control':
					ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(1.2, 1.03), loc='lower right', fontsize=40, handlelength=2, labelspacing=.15)
				else: 
					ax1.legend(h1+h2, l1+l2, loc='upper right', fontsize=40, handlelength=2, labelspacing=.15)

			ax1.set_ylim(fill_min,fill_max)

			ax1.set_ylabel(y_title, fontsize = 48)

			if section == 'Flow_vs_Shutdown':
				if exp in ['Experiment_1_Data', 'Experiment_12_Data', 'Experiment_17_Data']:
					ax1.set_ylim([fill_min*1.25, fill_max*1.25])
					ax1.legend(loc='upper right', fontsize=40, handlelength=3, labelspacing=.15)
					plt.subplots_adjust(top=.9)

			if not os.path.exists(output_location_section +  exp[:-5] + '/'):
				os.makedirs(output_location_section +  exp[:-5] + '/')

			# plt.show()
			# exit()
			
			plt.savefig(output_location_section +  exp[:-5] + '/' + sensor +'.pdf')
		plt.close('all')

print ('---------------------------------Plotting Thermal Classes Plot -----------------------------')

experiments = ['Experiment_1_Data', 'Experiment_12_Data', 'Experiment_14_Data']

channels = pd.DataFrame({'Location':['End Hall 1 FT', 'End Hall 3 FT', 'End Hall 5 FT', 'Mid Hall 1 FT', 'Start Hall 1 FT'], 
						'Temp':['3TC1','3TC3','3TC5','4TC1','5TC1'], 
						'Heat_Flux':['1HF1','1HF3','1HF5','2HF','3HF']})


vent_info = pd.read_csv(info_location + 'Vent_Info_Events.csv').set_index('Event')

times = {'Experiment_1_Data':408, 'Experiment_12_Data':324, 'Experiment_14_Data':312}

plot_data = {}

for exp in experiments:
	data_temp = []
	data_HF = []
	location = []
	for chan in channels.index:

		location.append(channels['Location'][chan])
		# data_temp.append((all_exp_data[exp][channels['Temp'][chan]][times[exp]:times[exp]+60].mean()-32)*5/9)
		data_temp.append(all_exp_data[exp][channels['Temp'][chan]][times[exp]:times[exp]+60].mean())
		data_HF.append(all_exp_data[exp][channels['Heat_Flux'][chan]][times[exp]:times[exp]+60].mean())

	plot_data[exp] = list(zip(location, data_HF, data_temp))

for exp in experiments:
	print ('Plotting ' + exp.replace('_', ' '))
	fig = plt.figure()
	fig.set_size_inches(8, 6)
	ax = plt.gca()

	ax.set_xlabel('Heat Flux (kW/m$^2$)',fontsize=16)
	ax.set_ylabel('Temperature ($^{\circ}$F)',fontsize=16)
	ax.set_axisbelow(True)
	plt.grid(linestyle='-',linewidth = 1.5)
	ax.set_xscale('log')
	ax.set_yscale('log')
	ax.set_xlim([.1,200])
	ax.set_ylim([(10*(9/5)+32),1200*(9/5)+32])
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	for axis in [ax.xaxis, ax.yaxis]:
			 axis.set_major_formatter(ScalarFormatter())

	plt.fill_between([0,200],[(10*(9/5)+32),(10*(9/5)-32)],[(1200*(9/5)+32),(1200*(9/5)+32)], color = 'r',alpha=0.4)
	plt.fill_between([12,200],[(200*(9/5)+32),(200*(9/5)+32)],[(1200*(9/5)+32),(1200*(9/5)+32)], color = 'r',alpha=0.86)
	plt.text(60, 430*(9/5)+32, 'EMERGENCY', va='center', ha='center', color='white', fontsize=16)

	plt.fill_between([0,12],[(10*(9/5)+32),(10*(9/5)+32)],[(200*(9/5)+32), (200*(9/5)+32)], color = 'w')
	plt.fill_between([0,12],[(10*(9/5)+32),(10*(9/5)+32)],[(200*(9/5)+32), (200*(9/5)+32)], color = 'y', alpha = 0.4)
	plt.fill_between([2,12],[(70*(9/5)+32),(70*(9/5)+32)],[(200*(9/5)+32), (200*(9/5)+32)], color = 'y',alpha=0.85)
	plt.text(4.75, 115*(9/5)+32, 'ORDINARY', va='center', ha='center', color='white', fontsize=16)

	plt.fill_between([0,2], [(10*(9/5)+32),(10*(9/5)+32)], [(70*(9/5)+32),(70*(9/5)+32)], color = 'w')
	plt.fill_between([0,2], [(10*(9/5)+32),(10*(9/5)+32)], [(70*(9/5)+32),(70*(9/5)+32)], color = 'g', alpha = 0.4)
	plt.fill_between([1,2], [(20*(9/5)+32),(20*(9/5)+32)], [(70*(9/5)+32),(70*(9/5)+32)], color = 'g' , alpha=0.85)
	plt.text(1.4, 39*(9/5)+32,'R\nO\nU\nT\nI\nN\nE', va='center', ha='center', color='white', fontsize=16, linespacing=.8)

	# Plot style - cycle through 20 color pallet and define markers to cycle through
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	for point in plot_data[exp]:
		plt.plot(point[1],point[2], label = point[0], marker = next(plot_markers), color='black', markersize = 10, linestyle='none' )
		# plt.text(point[1],point[2], exp[11:-5], va='center', ha='center', color = 'w', fontsize=10)

	plt.legend(channels['Location'].tolist(), numpoints=1, loc='upper left')
	fig.set_size_inches(10, 7)
	plt.tight_layout()	

	if not os.path.exists(output_location + '/Thermal_Class/'):
		os.makedirs(output_location + '/Thermal_Class/')

	plt.savefig(output_location + '/Thermal_Class/'  + exp[:-4] + 'Thermal_Exposure.pdf')
	plt.close('all')

