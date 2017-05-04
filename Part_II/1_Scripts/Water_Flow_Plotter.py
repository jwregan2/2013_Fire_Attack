import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

data_location = '../2_Data/'

info_file = '../3_Info/Water_Flow_Info.csv'

output_location = '../0_Images/Script_Figures/Water_Flow/'

vent_info = pd.read_csv(info_file)

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
print ('------------ Ploting Bar Charts for Vent Configuration ------------------')


width = 1 


colors = ['blue', 'green', 'red', 'orange', 'purple']
plt_colors = pd.DataFrame({'Vent_Type':vent_info.columns.values, 'Colors':colors}).set_index('Vent_Type')


start = 0

labels = []
labels_x = []

for vent in vent_info:

	print (vent.replace('_',' '))
	data = []

	for exp in vent_info[vent].dropna():

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

plt.xticks([x-2.5 for x in labels_x], labels, rotation = 45, fontsize = 16 )
plt.subplots_adjust(bottom=0.35)
plt.ylabel('Total Gallons', fontsize=18)
plt.savefig(output_location + 'Water_Flow' +'.pdf')
plt.close('all')


