import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
import shutil
# from bokeh.charts import Scatter, output_file, show
from dateutil.relativedelta import relativedelta
# from bokeh.plotting import figure, output_file, show, save
# from bokeh.models import HoverTool, Range1d, Span
from scipy.signal import butter, filtfilt
from itertools import cycle

#Define filter for low pass filtering of pressure/temperature for BDP
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filtfilt(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
			(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
			(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
			(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
			(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

#Set file locations

data_location = '../2_Data/'

channel_location = '../3_Info/'

chart_location = '../3_Info/'

output_location_init = '../0_Images/Results/'

# info_file = '../3_Info/Description_of_Experiments.csv'

# Read in channel list
channel_list = pd.read_csv(channel_location+'Channels.csv')

#Set index value for channels as 'Channel'
channel_list = channel_list.set_index('Channel')

#Create charts data by grouping channels for 'Chart'
channels = channel_list.groupby('Chart')

#Read in calculated channels
calculated_channels_list = pd.read_csv(channel_location+'Calculated_Channels.csv')

#Read in calculated channels
calculated_channels_list = calculated_channels_list.set_index('Title')

#Group calculated channels by 'Chart'
calculated_channels = calculated_channels_list.groupby('Chart')

#Read in Charts
chart_list = pd.read_csv(channel_location+'Charts.csv')

#Set index of chart list to the chart name.
charts = chart_list.set_index('Chart')

skip_files = ['example']

# Loop through Experiment files
for f in os.listdir(data_location):
	if f.endswith('.csv'):
		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue

		#Read in experiment file
		experiment = f
		exp = experiment[11:-9]
		Exp_Data = pd.read_csv(data_location + experiment)
		#Get Experiment Name from File
		Test_Name = experiment[:-4]

		output_location = output_location_init + Test_Name + '/'

		#If the folder exists delete it.
		if os.path.exists(output_location):
			shutil.rmtree(output_location)

		#If the folder doesn't exist create it.
		if not os.path.exists(output_location):
			os.makedirs(output_location)

		#Read in Experiment Events
		Events = pd.read_csv(channel_location + '/Events/' + Test_Name[:-4] + 'Events.csv')

		Events = Events.set_index('Event')

		#Get End of Experiment Time
		End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60

		print (Test_Name)
		
		for chart in charts.index:
			
			if charts['Type'][chart] == 'DualAxis':

				# create a new plot with a title and axis labels
				fig = plt.subplots()
            	# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
				tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
							(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
							(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
							(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
							(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

				for i in range(len(tableau20)):
					r, g, b = tableau20[i]
					tableau20[i] = (r / 255., g / 255., b / 255.)
				plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
				plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])
				xlim ([0,End_Time])
				
				#Set time to elapsed time column in experimental data and pull ignition time from events csv file.
				Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
				Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

				#Setting time equal to the elapsed time minus the ignition time which yields a test time with ignition a 0 seconds/minutes.
				Time = [((t - Ignition).total_seconds())/60 for t in Time]

				print ('Plotting ' + chart.replace('_',' '))
				for channel in channels.get_group(chart).index.values:
					scale_factor = channel_list['ScaleFactor'][channel]
					offset = channel_list['Offset'][channel]

					data = Exp_Data[channel] * scale_factor + offset
					data_c = (5.0/9.0)*(data-32.0)
					plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
					plt.plot(Time, data, linewidth=2, label=channel, marker=next(plot_markers), markevery=int(End_Time*60/50))
					ax1 = plt.gca()
					ax1.set_xlabel('Time (min)')
					ax1.set_ylabel(charts['Y_Label'][chart])
					ax1.set_ylim ([charts['Y_Min'][chart],charts['Y_Max'][chart]])
					plt.legend(loc='upper left')
				ax2 = ax1.twinx()
				ax2.set_ylim([charts['Secondary_Y_Min'][chart],charts['Secondary_Y_Max'][chart]])
				ax2.set_ylabel(charts['Secondary_Y_Label'][chart])
				# plt.title(Test_Name.replace('_',' ') + ' ' + chart.replace('_',' '))

				for event in Events.index.values:
					if not event == 'Ignition' and not event =='End Experiment':
						EventTime = (datetime.datetime.strptime(Events['Time'][event], '%H:%M:%S')-Ignition).total_seconds()
						plt.axvline(EventTime/60, color='0.5', lw=1)
						plt.text(EventTime/60, charts['Y_Max'][chart]*.95, [event], rotation=60, horizontalalignment='right')

				plt.savefig(output_location + chart + '.pdf')
				plt.close('all')

			if charts['Type'][chart] == 'Standard':

				# create a new plot with a title and axis labels
				fig = plt.figure()
            	# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
				tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
							(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
							(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
							(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
							(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

				for i in range(len(tableau20)):
					r, g, b = tableau20[i]
					tableau20[i] = (r / 255., g / 255., b / 255.)
				plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
				plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])
				xlim ([0,End_Time])
				ylim ([charts['Y_Min'][chart],charts['Y_Max'][chart]])

				#Set time to elapsed time column in experimental data and pull ignition time from events csv file.
				Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
				Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

				#Setting time equal to the elapsed time minus the ignition time which yields a test time with ignition a 0 seconds/minutes.
				Time = [((t - Ignition).total_seconds())/60 for t in Time]

				print ('Plotting ' + chart.replace('_',' '))
				for channel in channels.get_group(chart).index.values:
					scale_factor = channel_list['ScaleFactor'][channel]
					offset = channel_list['Offset'][channel]

					data = Exp_Data[channel] * scale_factor + offset

					plt.plot(Time, data, linewidth=2,label=channel,
								marker=next(plot_markers),markevery=int(End_Time*60/50))
					plt.xlabel('Time (min)')
					plt.ylabel(charts['Y_Label'][chart])
					# plt.title(Test_Name.replace('_',' ') + ' ' + chart.replace('_',' '))
					plt.legend(loc='upper left')

				for event in Events.index.values:
					if not event == 'Ignition' and not event =='End Experiment':
						EventTime = (datetime.datetime.strptime(Events['Time'][event], '%H:%M:%S')-Ignition).total_seconds()
						plt.axvline(EventTime/60, color='0.5', lw=1)
						plt.text(EventTime/60, charts['Y_Max'][chart]*.95, [event], rotation=60, horizontalalignment='right')

				plt.savefig(output_location + chart + '.pdf')
				plt.close('all')
				
			if charts['Type'][chart] == 'Calculated':

				# create a new plot with a title and axis labels
				fig = plt.figure()

				tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
							(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
							(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
							(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
							(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

            	# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
				for i in range(len(tableau20)):
					r, g, b = tableau20[i]
					tableau20[i] = (r / 255., g / 255., b / 255.)
				plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
				plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])
				xlim ([0,End_Time])
				ylim ([charts['Y_Min'][chart],charts['Y_Max'][chart]])

				#Set time to elapsed time column in experimental data and pull ignition time from events csv file.
				Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
				Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

				#Setting time equal to the elapsed time minus the ignition time which yields a test time with ignition a 0 seconds/minutes.
				Time = [((t - Ignition).total_seconds())/60 for t in Time]

				print ('Plotting ' + chart.replace('_',' '))

				for channel in calculated_channels.get_group(chart).index.values:
					
					#Get Channel Names from Calculated Channels List
					temp = calculated_channels_list['Temperature'][channel]
					press = calculated_channels_list['Pressure'][channel] 

					#Set Temperature Data
					temp_data = Exp_Data[press]
					# temp_data = butter_lowpass_filtfilt(Exp_Data[temp],calculated_channels_list['cutoff'][channel], calculated_channels_list['fs'][channel])
					
					#Set Pressure Data and filter
					press_data = Exp_Data[press]
					press_data = press_data - np.average(press_data[:90]) + 2.5
					press_data = butter_lowpass_filtfilt(press_data, calculated_channels_list['cutoff'][channel], calculated_channels_list['fs'][channel])

					#Calculate result
					data = np.sign(press_data-2.5)*0.070*((temp_data+273.15)*(99.6*abs(press_data-2.5)))**0.5

					plt.plot(Time, data, linewidth=2,label=channel,
								marker=next(plot_markers),markevery=int(End_Time*60/50))
					plt.xlabel('Time (min)')
					plt.ylabel(charts['Y_Label'][chart])
					# plt.title(Test_Name.replace('_',' ') + ' ' + chart.replace('_',' '))
					plt.legend(loc='upper left')

				for event in Events.index.values:
					if not event == 'Ignition' and not event =='End Experiment':
						EventTime = (datetime.datetime.strptime(Events['Time'][event], '%H:%M:%S')-Ignition).total_seconds()
						plt.axvline(EventTime/60, color='0.5', lw=1)
						plt.text(EventTime/60, charts['Y_Max'][chart]*.95, [event], rotation=60, horizontalalignment='right')

				plt.savefig(output_location + chart + '.pdf')
				plt.close('all')