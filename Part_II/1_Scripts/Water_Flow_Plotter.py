import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

data_location = '../2_Data/'

tactic_info = pd.read_csv('../3_Info/Water_Flow_Info.csv')

vent_info = pd.read_csv('../3_Info/Vent_Info.csv')

output_location = '../0_Images/Script_Figures/Water_Flow/'

all_flow_data = {}

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

colors = ['blue', 'green', 'red', 'orange', 'purple']
plt_colors = pd.DataFrame({'Vent_Type':tactic_info.columns.values, 'Colors':colors}).set_index('Vent_Type')

width = 1

start = 0

labels = []
labels_x = []

for vent in tactic_info:

	print (vent.replace('_',' '))
	data = []

	for exp in tactic_info[vent].dropna():

		if exp[:-4] + 'Flow' in all_flow_data:
			data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))

	x = np.arange(start,start+len(data)) + width/2

	plt.bar(x, data, width, label = f[-8].replace('_', ' '), color=plt_colors['Colors'][vent])
	x_start = x[0]
	x_end = x[-1]+width 

	plt.plot([x_start,x_end],[np.average(data),np.average(data)], color='black', lw=2)
	labels.append(vent.replace('_',' ')) 

	labels_x.append(np.average(x))
	start = start + len(data)
	end = x_end

plt.xticks([x-2.5 for x in labels_x], labels, rotation = 45, fontsize = 16 )
plt.xlim([0 , end + 0.5*width])
plt.subplots_adjust(bottom=0.35)
plt.ylabel('Total Gallons', fontsize=18)
plt.savefig(output_location + 'Water_Flow' +'.pdf')
plt.close('all')

#Print bar charts by vent configuration. 

print ('------------ Flow Data by Vent Configuration ------------------')

for vent in vent_info:
	print (vent)
	num_exp = len (vent_info[vent].dropna())
	
	
	width = .85
	# plt.figure(figsize=((num_exp+1)*width,5))
	plt.style.use('ggplot')

	x = np.arange(0,width*num_exp,width)

	data = []
	labels = []

	for exp in vent_info[vent].dropna():
		
		if exp[:-4]+'Flow' not in all_flow_data.keys():
			x = x[:-1]
			print ('Dropped x for' + exp)
			continue	
		
		data.append(np.round(all_flow_data[exp[:-4] + 'Flow']['Total Gallons'].max(),2))
		labels.append(exp[:-5].replace('_',' '))

	plt.xticks(x+.5*width, labels, rotation = 45, fontsize = 16 )
	plt.xlim([0,len(x)+1])
	plt.subplots_adjust(bottom=0.30)
	plt.ylabel('Total Gallons', fontsize=18)
	plt.yticks(fontsize=16)
	plt.bar(x+.5*width, data, width)	
	plt.plot([x[0]+.5*width, x.max()+.5*width+1], [np.average(data), np.average(data)], lw=2, color='black')
	plt.savefig(output_location + vent +'.pdf')
	plt.close('all')


