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

chart_location = '../../Report/Script_Figures/Entrainment/'

info_file = '../Info/description_of_experiments_entrainment.csv'
plot_file = '../Info/description_of_charts.csv'

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Test_Name')
# Set files to skip in experimental directory
skip_files = ['_events']

channels_nr = ['BDP1V','BDP2V','BDP3V','BDP4V','BDP5V']
channels_hr = ['BDP1VHR','BDP2VHR','BDP3VHR','BDP4VHR','BDP5VHR']

# Loop through Experiment files
for f in os.listdir(data_location):
	if f.endswith('.csv'):

		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue

		# Read in experiment file
		experiment = f

		# exp = experiment[11:-9]
		Exp_Data = pd.read_csv(data_location + experiment)
		data_copy = Exp_Data.drop('Elapsed Time', axis=1)
		data_copy = data_copy.rolling(window=1, center=True).mean()
		data_copy.insert(0, 'Elapsed Time', Exp_Data['Elapsed Time'])
		data_copy = data_copy.dropna()
		Exp_Data = data_copy

		Exp_Events = pd.read_csv(data_location + experiment[:-4]+'_Events.csv')
		Event_Time = [datetime.datetime.strptime(t, '%Y-%m-%d-%H:%M:%S') for t in Exp_Events['Time']]

		# Get experiment name from file
		Test_Name = experiment[:-4]
		Exp_Num = Test_Name[4:-7]

		temp_time = []
		for i in range(len(Event_Time)):
			temp_time.append(Event_Time[i].timestamp() - Event_Time[0].timestamp())
		Exp_Events['Elapsed_Time'] = temp_time
		Start_Time = Exp_Events['Elapsed_Time'][0]
		End_Time = temp_time[-1]

		BDP_Resolution = Exp_Des['BDP_Res'][Test_Name]
		if BDP_Resolution == 'N':
			channels = channels_nr
			conv_inch_h2o = 0.04
		else:
			channels = channels_hr
			conv_inch_h2o = 0.2

		print (Test_Name)

		area = 17.778
		for channel in channels:
			#Calculate velocity
			conv_pascal = 248.84
			convert_ftpm = 196.85
			end_zero_time = int(Exp_Events['Elapsed_Time'][1])
			zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
			pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel])  # Convert voltage to pascals
			# Calculate flowrate
			Exp_Data[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * ((Exp_Des['Temp_C'][Test_Name])+273.13)) * np.sign(pressure)

		#Calculate cfm
		if int(Exp_Num) < 18:
			CFM = area*(Exp_Data[[channels[0],channels[2],channels[3]]].mean(axis=1))
			CFM_1 = area*(Exp_Data[channels[2]])
			CFM_3 = area*(Exp_Data[[channels[2],channels[3]]].mean(axis=1))
		else:
			CFM = area*np.mean(Exp_Data[channels],axis=1)
			CFM_1 = area*(Exp_Data[channels[2]])
			CFM_3 = area*np.mean(Exp_Data[channels[1:3]],axis=1)
		zero_CFM = np.mean(CFM[0:end_zero_time])
		zero_CFM_1 = np.mean(CFM_1[0:end_zero_time])
		zero_CFM_3 = np.mean(CFM_3[0:end_zero_time])
		CFM = CFM - zero_CFM
		CFM_1 = CFM_1 - zero_CFM_1
		CFM_3 = CFM_3 - zero_CFM_3
		cfm_avgs = []
		for i in range(1,len(Exp_Events)):
			pos2 = int(Exp_Events['Elapsed_Time'][i])
			pos1 = int(Exp_Events['Elapsed_Time'][i-1])
			cfm_avgs.append(np.mean(CFM[pos1:pos2]))
		cfm_avgs = np.append(cfm_avgs,'NaN')
		Exp_Events['CFM_Avg'] = cfm_avgs
		Exp_Events.to_csv('../Experimental_Data/'+ Test_Name + '_Events_CFM.csv')
		time = list(range(len(Exp_Data)))

		fig = figure()
		plt.plot(time,CFM,'k-',label='CFM All')
		plt.plot(time,CFM_3,'b--',label='CFM Middle 3')
		plt.plot(time,CFM_1,'r-.',label='CFM Middle')
		ax1 = plt.gca()
		handles1, labels1 = ax1.get_legend_handles_labels()
		ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
		ax1_xlims = ax1.axis()[0:2]
		plt.xlim([0, End_Time-Start_Time])
		plt.xlabel('Time (s)')
		plt.ylabel('CFM (ft$^3$/min)')
		try:
			# Add vertical lines and labels for timing information (if available)
			ax3 = ax1.twiny()
			ax3.set_xlim(ax1_xlims)
			# Remove NaN items from event timeline
			events = Exp_Events['Event']
			[plt.axvline(_x, color='0.50', lw=1) for _x in Exp_Events['Elapsed_Time']]
			ax3.set_xticks(Exp_Events['Elapsed_Time'])
			plt.setp(plt.xticks()[1], rotation=60)
			ax3.set_xticklabels(events.values, fontsize=8, ha='left')
			plt.xlim([0, End_Time])
			# Increase figure size for plot labels at top
			fig.set_size_inches(10, 9)
		except:
			pass
		plt.legend(handles1, labels1, loc='upper left', fontsize=12, handlelength=3)
		savefig(chart_location+Test_Name+'_CFM.pdf')
		close()

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
	print('Plotting: ' + plot_file['Chart_Title'][k])
	test_comps=[]
	event_nums=[]
	legend_names = []
	event_nums_anomoly = []
	temp1 = plot_file['Experiments_To_Compare'][k].split('|')
	test_comps = np.asarray(temp1)
	if plot_file['Anomalies'][k] == 0:
		temp2 = plot_file['Bars'][k].split('|')
		event_nums = np.asarray(temp2)
	elif plot_file['Anomalies'][k] == 1:
		temp2 = plot_file['Bars'][k].split('|')
		event_nums = np.asarray(temp2)
		temp3 = plot_file['New_Bars'][k].split('|')
		event_nums_anomaly = np.asarray(temp3)
		temp4 = plot_file['Anomaly_Exp'][k].split('|')
		test_anomaly = np.asarray(temp4)
	temp5 = plot_file['Legend'][k].split('|')
	legend_names = np.asarray(temp5)
	file_name = plot_file['Plot_Name'][k]

	ind = np.arange(len(event_nums))  # the x locations for the groups
	width = 0.8/len(test_comps)  # the width of the bars

	fig, ax = plt.subplots(figsize=(10, 9))
	cfm_bars = np.zeros((len(test_comps),len(event_nums)))
	labels = ["" for x in range(len(event_nums))]
	for i in range(len(test_comps)):
		temp_read = pd.read_csv('../Experimental_Data/'+test_comps[i]+'_Events_CFM.csv')
		for j in range(len(event_nums)):
			if plot_file['Anomalies'][k] == 0:
				cfm_bars[i,j] = temp_read['CFM_Avg'][int(event_nums[j])]
				labels[j] = temp_read['Event'][int(event_nums[j])]
			elif plot_file['Anomalies'][k] == 1:
				if test_comps[i] in test_anomaly[:]:
					cfm_bars[i,j] = temp_read['CFM_Avg'][int(event_nums_anomaly[j])]
				else:
					cfm_bars[i,j] = temp_read['CFM_Avg'][int(event_nums[j])]
					labels[j] = temp_read['Event'][int(event_nums[j])]
		rects = ax.bar(ind+i*width, cfm_bars[i,:], width, color=tableau20[i])

	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
	ax.legend(legend_names,loc='center left', bbox_to_anchor=(1, 0.5))
	ax.set_title(plot_file['Chart_Title'][k])
	ax.set_ylabel('CFM')
	if len(test_comps) == 1:
		ax.set_xticks(ind + width/2)
	else:
		ax.set_xticks(ind + width)
	ax.set_xticklabels(labels, rotation = -15, ha = 'left')
	savefig(chart_location+file_name+'.pdf')

	plt.close('all')