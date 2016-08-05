import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
from dateutil.relativedelta import relativedelta
from itertools import cycle

# Set file locations

data_location = '../Experimental_Data/'

chart_location = '../Figures/'

info_file = '../description_of_experiments_entrainment.csv'
plot_file = '../description_of_charts.csv'

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Test_Name')
# Set files to skip in experimental directory
skip_files = ['_events']

channels_nr = ['BDP1V','BDP2V','BDP3V','BDP4V','BDP5V']
channels_hr = ['BDP1VHR','BDP2VHR','BDP3VHR','BDP4VHR','BDP5VHR']

# # Loop through Experiment files
# for f in os.listdir(data_location):
# 	if f.endswith('.csv'):

# 		# Skip files with time information or reduced data files
# 		if any([substring in f.lower() for substring in skip_files]):
# 			continue

# 		# Read in experiment file
# 		experiment = f

# 		# exp = experiment[11:-9]
# 		Exp_Data = pd.read_csv(data_location + experiment)
# 		data_copy = Exp_Data.drop('Elapsed Time', axis=1)
# 		data_copy = data_copy.rolling(window=10, center=True).mean()
# 		data_copy.insert(0, 'Elapsed Time', Exp_Data['Elapsed Time'])
# 		data_copy = data_copy.dropna()
# 		Exp_Data = data_copy

# 		Exp_Events = pd.read_csv(data_location + experiment[:-4]+'_Events.csv')
# 		Event_Time = [datetime.datetime.strptime(t, '%Y-%m-%d-%H:%M:%S') for t in Exp_Events['Time']]

# 		# Get experiment name from file
# 		Test_Name = experiment[:-4]
# 		Exp_Num = Test_Name[4:-7]

# 		temp_time = []
# 		for i in range(len(Event_Time)):
# 			temp_time.append(Event_Time[i].timestamp() - Event_Time[0].timestamp() + Exp_Des['Time_Offset'][Test_Name])
# 		Exp_Events['Elapsed_Time'] = temp_time

# 		BDP_Resolution = Exp_Des['BDP_Res'][Test_Name]
# 		if BDP_Resolution == 'N':
# 			channels = channels_nr
# 		else:
# 			channels = channels_hr

# 		print ()
# 		print (Test_Name)

# 		for channel in channels:
# 			#Calculate velocity
# 			conv_inch_h2o = 0.4
# 			conv_pascal = 248.8
# 			convert_ftpm = 196.85
# 			end_zero_time = int(Exp_Events['Elapsed_Time'][1])
# 			zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
# 			pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel] - zero_voltage)  # Convert voltage to pascals
# 			# Calculate velocity
# 			Exp_Data[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * (293.15)) * np.sign(pressure)

# 		#Calculate cfm
# 		area = 18.56
# 		CFM = np.mean(Exp_Data[channels],axis=1)*area
# 		cfm_avgs = []
# 		for i in range(1,len(Exp_Events)):
# 			pos2 = int(Exp_Events['Elapsed_Time'][i])
# 			pos1 = int(Exp_Events['Elapsed_Time'][i-1])
# 			cfm_avgs.append(np.mean(CFM[pos1:pos2]))
# 		cfm_avgs = np.append(cfm_avgs,'NaN')
# 		Exp_Events['CFM_Avg'] = cfm_avgs

# 		Exp_Events.to_csv('../Experimental_Data/'+ Test_Name + '_Events_CFM.csv')

tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(tableau20)):
    r, g, b = tableau20[i]
    tableau20[i] = (r / 255., g / 255., b / 255.)


#Plotting
plot_file = pd.read_csv(plot_file)

for k in range(len(plot_file)):
	test_comps=[]
	event_nums=[]
	legend_names = []
	temp1 = plot_file['Experiments_To_Compare'][k].split('|')
	test_comps = np.asarray(temp1)
	if plot_file['Anomalies'][k] == 0:
		temp2 = plot_file['Bars'][k].split('|')
	elif plot_file['Anomalies'][k] == 1:
		temp2 = plot_file['New_Bars'][k].split('|')
	event_nums = np.asarray(temp2)
	temp3 = plot_file['Legend'][k].split('|')
	legend_names = np.asarray(temp3)
	file_name = plot_file['Plot_Name'][k]
	
	ind = np.arange(len(event_nums))  # the x locations for the groups
	width = 0.8/len(test_comps)  # the width of the bars
	fig, ax = plt.subplots()

	cfm_bars = np.zeros((len(test_comps),len(event_nums)))
	labels = ["" for x in range(len(event_nums))]
	for i in range(len(test_comps)):
		temp_read = pd.read_csv('../Experimental_Data/'+test_comps[i]+'_Events_CFM.csv')
		for j in range(len(event_nums)):
			cfm_bars[i,j] = temp_read['CFM_Avg'][int(event_nums[j])]
			labels[j] = temp_read['Event'][int(event_nums[j])]

		rects = ax.bar(ind+i*width, cfm_bars[i,:], width, color=tableau20[i])

	ax.legend(legend_names)
	ax.set_title(plot_file['Chart_Title'][k])
	ax.set_ylabel('CFM')
	ax.set_xticks(ind + width)
	ax.set_xticklabels(labels)
	savefig('../Figures/'+file_name+'.png')

	plt.close('all')