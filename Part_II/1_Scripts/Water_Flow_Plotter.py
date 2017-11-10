import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from itertools import cycle
import matplotlib.transforms as mtransforms
from pylab import * 
import pickle


data_location = '../2_Data/'

info_location = '../3_Info/'

tactic_info = pd.read_csv('../3_Info/Water_Flow_Info.csv')

vent_info = pd.read_csv('../3_Info/Vent_Info.csv')

output_location = '../0_Images/Script_Figures/Water_Flow/'

all_flow_data = {}

# Define 20 color pallet using RGB values
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# # Define 20 color pallet using RGB values
# tableau20 = [(255, 127, 14), (255, 187, 120), 
# (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
# (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
# (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
# (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Define RGB values in pallet 
for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b / 255.)

plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
prop_iter = iter(plt.rcParams['axes.prop_cycle'])

for f in os.listdir(data_location):
	if f.endswith('csv'):
		if 'Flow' in f:
			print ('-------Reading ' + f[:-8].replace('_', ' ') + 'Flow Data -------')
			all_flow_data[f[:-4]]=pd.read_csv(data_location + f)

# ------------------------------- Plot Bar Charts by Ventilation Configuration ---------------------

if not os.path.exists(output_location):
    os.makedirs(output_location)
print ('\n')
print ('------------ All Flow Data ------------------')

width = 1

start = 0.5

labels = []
labels_x = []
labels_pos = []

fig = plt.figure()
fig.set_size_inches(8, 6)
matplotlib.rcParams.update({'font.size':18})

for vent in tactic_info:

	print (vent.replace('_',' '))
	data = []

	for exp in tactic_info[vent].dropna():

		if exp[:-4] + 'Flow' in all_flow_data:
			data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))

	x = np.arange(start,start+len(data)) + width/2

	plt.bar(x, data, width, label = 'Average: ' + str(int(np.average(data))) + ' gal.', color=next(prop_iter)['color'])
	x_start = x[0]
	x_end = x[-1]+width 

	# plt.plot([x_start,x_end],[np.average(data),np.average(data)], color='black', lw=2)
	labels.append(vent.replace('_',' '))

	labels_pos.append(np.average([x_end,x_start])) 

	labels_x.append(np.average(x))
	start = start + len(data)
	end = x_end

plt.legend(bbox_to_anchor=(1.01 , .8), loc='upper left', ncol=1, fontsize = 16)
plt.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='on')
plt.xticks(labels_pos, labels, rotation = 45, fontsize = 16, horizontalalignment='right' )
plt.xlim([0 , end])
plt.subplots_adjust(bottom=0.35, right=0.625)
plt.ylabel('Total Gallons', fontsize=18)
plt.savefig(output_location + 'Water_Flow' +'.pdf')
plt.close('all')

#Print bar charts by vent configuration. 

print ('------------ Flow Data by Vent Configuration ------------------')

for vent in tactic_info:

	fig = plt.figure()
	fig.set_size_inches(8, 6)

	print (vent)
	num_exp = len (tactic_info[vent].dropna())
	
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	prop_iter = iter(plt.rcParams['axes.prop_cycle'])

	width = 1
	# plt.figure(figsize=((num_exp+1)*width,5))
	# plt.style.use('ggplot')

	# x = np.arange(0,width*num_exp,width)
	x = .5
	data = []
	labels = []

	for exp in tactic_info[vent].dropna():
		
		if exp[:-4]+'Flow' not in all_flow_data.keys():
			continue	

		plt.bar(x+.5, np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2), width, label = exp[:-5].replace('_',' '),color=next(prop_iter)['color'])

		if exp == 'Experiment_22_Data':
			pos = -18
		else: 
			pos = -12
		plt.text(x+.5*width, np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2)+pos, str(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),1) ), ha='center')
		
		data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))
		x = x + width

	plt.xlim([0,len(data)+1])
	plt.text((len(data)+1)/2,275, 'Average Flow ' + str(np.round(np.average(data),1)), ha='center')
	plt.plot([.5, len(data)+.5*width], [np.average(data), np.average(data)], lw=2, color='black')
	plt.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='off')
	plt.ylim([0,300])
	plt.subplots_adjust(right=0.65)
	plt.legend(bbox_to_anchor=(1.01 , .8), loc='upper left', ncol=1, fontsize = 16, title = vent.replace('_',' '))
	plt.ylabel('Total Gallons', fontsize=18)
	plt.yticks(fontsize=16)
	plt.savefig(output_location + vent +'.pdf')
	plt.close('all')

print ('------------ Plotting Flow & Move Vs. Shutdown and Move ------------------')

vents = ['No_Vent', 'Single_Vent', 'Two_Vent']

flow_move = {'No_Vent':['Experiment_2_Flow', 'Experiment_4_Flow'], 
			'Single_Vent':['Experiment_7_Flow','Experiment_9_Flow', 'Experiment_11_Flow', 'Experiment_12_Flow'], 
			'Two_Vent':['Experiment_13_Flow', 'Experiment_16_Flow', 'Experiment_17_Flow']}

shut_move = {'No_Vent':['Experiment_1_Flow', 'Experiment_3_Flow', 'Experiment_5_Flow', 'Experiemnt_6_Flow'], 
			'Single_Vent':['Experiment_8_Flow','Experiment_10_Flow'], 
			'Two_Vent':['Experiment_14_Flow', 'Experiment_15_Flow']}

width = 1

labels = []
label_pos = []
x_value = 0.5

plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
prop_iter = iter(plt.rcParams['axes.prop_cycle'])


fig = plt.figure()
fig.set_size_inches(9, 5)

for vent in vents:
	labels.append(vent.replace('_',' '))

	data = []
	x = []
	x_start = x_value

	for exp in flow_move[vent]:
		
		if exp in all_flow_data.keys():
			data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))
			x.append(x_value+.5)
			x_value = x_value + width

	plt.bar(x, data, width,color=tableau20[0])

	data =[]
	x=[]
	
	for exp in shut_move[vent]:
		if exp in all_flow_data.keys():
			data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))
			x.append(x_value+.5)
			x_value = x_value + width

	plt.bar(x, data, width, color=tableau20[2])

	x_end = x_value +.5

	label_pos.append(np.average([x_start,x_end]))
	x_value = x_value + 1

plt.xlim([0,x_end])
plt.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='on')

plt.xticks(label_pos, labels, rotation = 45, fontsize = 16, horizontalalignment='right')
plt.ylim([0,300])
plt.subplots_adjust(right=.60, bottom=0.25)
plt.legend(labels=['Flow and Move', 'Shutdown and Move'], bbox_to_anchor=(1.01 , .5), loc='center left', ncol=1, fontsize = 16)
plt.ylabel('Total Gallons', fontsize=18)
plt.yticks(fontsize=16)
plt.savefig(output_location + 'Flow_vs_Shutdown.pdf')
plt.close('all')

# print ('------------ Plotting Smoothboore Vs. Combination Nozzle  ------------------')

# Smoothboore = {'Flow_Move':'Experiment_7_Flow', 'Shut_Move':'Experiment_8_Flow'}

# Combination = {'Flow_Move':'Experiment_11_Flow', 'Shut_Move':'Experiment_10_Flow'}

# width = 1

# labels = []
# label_pos = []
# x_value = 0.5

# plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
# prop_iter = iter(plt.rcParams['axes.prop_cycle'])

# plt.figure(figsize=(9,5))

# for tactic in Smoothboore.keys():
# 	labels.append(tactic.replace('_',' '))

# 	data = []
# 	x = []
# 	x_start = x_value

# 	# for exp in Smoothboore[tactic]:
# 	exp = Smoothboore[tactic]

# 	if exp in all_flow_data.keys():	
# 		data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))
# 		x.append(x_value)
# 		x_value = x_value + width

# 	plt.bar(x, data, width,color=tableau20[0], label = tactic.replace('_',' '))

# 	data =[]
# 	x=[]
	
# 	exp = Combination[tactic]
# 	if exp in all_flow_data.keys():
# 		data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))
# 		x.append(x_value)
# 		x_value = x_value + width

# 	plts = plt.bar(x, data, width, color=tableau20[2], label = tactic.replace('_',' '))

# 	x_end = x_value

# 	label_pos.append(np.average([x_start,x_end]))
# 	x_value = x_value + 1

# plt.xlim([0,x_end+.5])
# plt.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='on')

# plt.xticks(label_pos, labels, rotation = 45, fontsize = 16, horizontalalignment='right')
# plt.ylim([0,300])
# plt.subplots_adjust(right=.60, bottom=0.25)
# plt.legend(labels=['SmoothBoore', 'Combination'], bbox_to_anchor=(1.01 , .5), loc='center left', ncol=1, fontsize = 16)
# plt.ylabel('Total Gallons', fontsize=18)
# plt.yticks(fontsize=16)
# plt.savefig(output_location + 'Single_Vent_SB_vs_Combo_Flow_Shut.pdf')
# plt.close('all')

print ('------------ Plotting Room Suppression Comparison ------------------')

tactics = ['From_Window', 'From_Door']

Suppression_Comp = {'From_Window':['Experiment_18_Data', 'Experiment_20_Data', 'Experiment_21_Data',], 
					'From_Door':['Experiment_8_Data', 'Experiment_10_Data']}

all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))

all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))

width = 1

labels = []
label_pos = []
x_value = 0.5

plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
prop_iter = iter(plt.rcParams['axes.prop_cycle'])

fig = plt.figure()
fig.set_size_inches(9, 5)

for tactic in tactics:
	labels.append(tactic.replace('_',' '))
	data = []
	x = []
	x_start = x_value
	x_end = 0

	for exp in Suppression_Comp[tactic]:
		
		if exp in all_flow_data.keys():	

			if tactic == 'From_Window':
				data.append(np.round(all_flow_data[exp]['Total Gallons'].max(),2))
			
			if tactic == 'From_Door':
				flow_start = 1
				
				for i in range(0,3):
					if i == 0:
						flow_data  = all_flow_data[exp]['GPM']
					
					flow_start = (flow_data>50).idxmax()
					flow_data = flow_data[flow_start:]
					flow_stop = (flow_data<10).idxmax()
					flow_data = flow_data[flow_stop:]

				data.append(np.round(all_flow_data[exp]['Total Gallons'][flow_start:].max() - all_flow_data[exp]['Total Gallons'][flow_start],2)) 

			x.append(x_value)
			x_end = x_value
			x_value = x_value + width

	label_pos.append(np.average([x_start,x_value]))

	plt.bar(x, data, width,color=next(prop_iter)['color'], label = tactic.replace('_',' ') + ' Average: ' + str(np.round(np.average(data),1)))

# plt.xlim([0,x_end+.5])
plt.tick_params(axis='x',which='both',bottom='off',top='off',labelbottom='on')
plt.xticks(label_pos, labels, rotation = 45, fontsize = 16, horizontalalignment='right')
plt.ylim([0,120])
plt.subplots_adjust(right=.50, bottom=0.27)
plt.legend(bbox_to_anchor=(1.01 , .5), loc='center left', ncol=1, fontsize = 16)
plt.ylabel('Total Gallons', fontsize=18)
plt.yticks(fontsize=16)
plt.savefig(output_location + 'Door_vs_Window.pdf')
plt.close('all')

exit()

print ('------------ Plotting All Waterflow by Experiment ------------------')

for exp in all_flow_data.keys():
	output_location = '../0_Images/Script_Figures/Water_Flow/All_Data/'
	
	if not os.path.exists(output_location):
	    os.makedirs(output_location)

	fig = plt.figure()
	fig.set_size_inches(8, 6)
	
	# plt.style.use('ggplot') 

	# Plot style - cycle through 20 color pallet and define markers to cycle through
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	ax1 = plt.gca()
	handles1, labels1 = ax1.get_legend_handles_labels()
	ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
	ax1_xlims = ax1.axis()[0:2]
	plt.grid(True)
	plt.xlabel('Time (min)', fontsize=32)
	plt.xticks(fontsize=28)
	plt.yticks(fontsize=28)
	plt.ylabel('Flow (GPM)', fontsize = 32)
	plt.ylim([0,300])
	ax1.plot(all_flow_data[exp].index.values/60, all_flow_data[exp]['GPM'], label = 'Flow Rate', lw = 2)
	
	ax2 = ax1.twinx()

	ax2.plot(all_flow_data[exp].index.values/60, all_flow_data[exp]['Total Gallons'], label= 'Total Gallons', lw=2, color='#1f77b4',)
	ax2.set_ylim(0,300)
	ax2.set_ylabel('Total Flow (Gallons)', fontsize=32)
	ax2.tick_params(axis='y', labelsize=28)

	h1, l1 = ax1.get_legend_handles_labels()
	h2, l2 = ax2.get_legend_handles_labels()
	ax1.legend(h1+h2, l1+l2, loc='upper right', fontsize=24, handlelength=3)

	plt.xlim([0,all_exp_events[exp[:-4]+'Events']['Time_Seconds']['End Experiment']/60])
	
	fig.set_size_inches(20, 16)

	plt.savefig(output_location + exp[:-4] + '.pdf')
	plt.close('all')
