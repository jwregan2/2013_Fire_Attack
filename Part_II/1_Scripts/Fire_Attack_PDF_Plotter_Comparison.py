import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle

# Define filter for low pass filtering of pressure/temperature for BDP
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filtfilt(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Define 20 color pallet using RGB values
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Define RGB values in pallet 
for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b / 255.)

# Set file locations

data_location = '../2_Data/Smaller_Data/'

channel_location = '../3_Info/'

chart_location = '../3_Info/'

output_location_init = '../0_Images/Results/Comparisons/'

info_file = '../3_Info/Description_of_Experiments.csv'

# Read in channel list
channel_list = pd.read_csv(channel_location+'Channels.csv')

# Set index value for channels as 'Channel'
channel_list = channel_list.set_index('Channel')

# Create groups data by grouping channels for 'Chart'
channel_groups = channel_list.groupby('Primary_Chart')
# channel_groups = channel_list.groupby('Secondary_Chart')

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)

# Set index of description of experiments to Experiment
Exp_Des = Exp_Des.set_index('Experiment')

# Set files to skip in experimental directory
skip_files = ['example']

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

		# Get experiment name from file
		Test_Name = experiment[:-4]

		# Grab experiment number from test name
		Exp_Num = Test_Name[:-5]

		comps = []
		temp = Exp_Des['Experiments To Compare'][Test_Name].split('|')
		comps = np.asarray(temp)
		for nn in range(len(comps)):
			print()
			print(Exp_Num + ' compare with Experiment_'+comps[nn])
			print()
			try:
				Exp_Data_2 = pd.read_csv(data_location + 'Experiment_' + str(comps[nn]) + '_Data.csv')
				Test_Name_2 = 'Experiment_'+str(comps[nn]) + '_Data'
				# Set output location for results
				output_location = output_location_init + Exp_Num + '_and_Experiment_' + str(comps[nn]) + '/'	

				# # If the folder exists delete it.
				# if os.path.exists(output_location):
				# 	shutil.rmtree(output_location)

				# # If the folder doesn't exist create it.
				if not os.path.exists(output_location):
					os.makedirs(output_location)

				# Get which house from description of events file
				House = Exp_Des['House'][Test_Name]
				House_2 = Exp_Des['House'][Test_Name_2]

				# Get which data speed from description of events file
				Speed = Exp_Des['Speed'][Test_Name]
				Speed_2 = Exp_Des['Speed'][Test_Name_2]

				# Read in each experiment event file
				Events = pd.read_csv(channel_location + '/Events/' + Test_Name[:-4] + 'Events.csv')
				Events_2 = pd.read_csv(channel_location + '/Events/' + Test_Name_2[:-4] + 'Events.csv')

				# Set index of experiment events files to Event
				Events = Events.set_index('Event')
				Events_2 = Events_2.set_index('Event')

				# If statements to determine whether or not data is in high speed and assigning time accordingly based on data csv
				if Speed == 'low':
					#Set time to elapsed time column in experimental data.
					Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
					mark_freq = 15
				elif Speed == 'high':
					Time = [datetime.datetime.strptime(t, '%M:%S.%f') for t in Exp_Data['Elapsed Time']]
					mark_freq = 5
				
				if Speed_2 == 'low':
					#Set time to elapsed time column in experimental data.
					Time_2 = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data_2['Elapsed Time']]
					mark_freq = 15
				elif Speed_2 == 'high':
					Time_2 = [datetime.datetime.strptime(t, '%M:%S.%f') for t in Exp_Data_2['Elapsed Time']]
					mark_freq = 5

				# Pull ignition time from events csv file
				Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')
				Ignition_2 = datetime.datetime.strptime(Events_2['Time']['Ignition'], '%H:%M:%S')

				# Adjust time for ignition offset
				Time = [((t - Ignition).total_seconds())/60 for t in Time]
				Time_2 = [((t - Ignition_2).total_seconds())/60 for t in Time_2]

				#Get End of Experiment Time
				End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60
				
				if House == 'a':
					scalefactor = 'ScaleFactor_A'
					Transport_Time = 'Transport_Time_A'
				elif House == 'b':
					scalefactor = 'ScaleFactor_B'
					Transport_Time = 'Transport_Time_B'

				if House_2 == 'a':
					scalefactor_2 = 'ScaleFactor_A'
					Transport_Time_2 = 'Transport_Time_A'
				elif House_2 == 'b':
					scalefactor_2 = 'ScaleFactor_B'
					Transport_Time_2 = 'Transport_Time_B'

				# Begin plotting

				for group in channel_groups.groups:
					# Skip excluded groups listed in test description file
					if any([substring in group for substring in Exp_Des['Excluded Groups'][Test_Name].split('|')]):
						continue

					#Create figure
					fig = plt.figure()

					# Plot style - cycle through 20 color pallet and define markers to cycle through
					plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
					plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

					# Print 'Plotting Chart XX'
					# print ('Plotting ' + group.replace('_',' '))

					# Begin cycling through channels
					for channel in channel_groups.get_group(group).index.values:

						# Skip plot quantity if channel name is blank
						if pd.isnull(channel):
							continue

						# Skip excluded channels listed in test description file
						if any([substring in channel for substring in Exp_Des['Excluded Channels'][Test_Name].split('|')]):
							continue

						# Set scale factor and offset
						scale_factor = channel_list[scalefactor][channel]
						scale_factor_2 = channel_list[scalefactor_2][channel]
						offset = channel_list['Offset'][channel]
						current_data = Exp_Data[channel]
						current_data_2 = Exp_Data_2[channel]
						# Set secondary axis default to None, unless otherwise stated below
						secondary_axis_label = None

						# Set parameters for temperature plots
						if channel_list['Type'][channel] == 'Temperature':
							Data_Time = Time
							Data_Time_2 = Time_2
							# Set data to include slope and intercept
							current_data = current_data * scale_factor + offset
							current_data_2 = current_data_2 * scale_factor_2 + offset
							plt.ylabel('Temperature ($^\circ$F)', fontsize = 16)
							if 'Skin' in group:
								axis_scale = 'Y Scale Skin Temperature'
							else: # Default to standard temperature scale
								axis_scale = 'Y Scale Temperature'
							secondary_axis_label = 'Temperature ($^\circ$C)'
							secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) * 5/9 - 32

						# Set parameters for velocity plots
						if channel_list['Type'][channel] == 'Velocity':
							Data_Time = Time
							Data_Time_2 = Time_2
							# Define cutoff and fs for filtering 
							cutoff = 50
							fs = 700
							current_data = current_data - np.average(current_data[:90]) + 2.5
							current_data = butter_lowpass_filtfilt(current_data, cutoff, fs)
							current_data_2 = current_data_2 - np.average(current_data_2[:90]) + 2.5
							current_data_2 = butter_lowpass_filtfilt(current_data_2, cutoff, fs)

							#Calculate result
							current_data = np.sign(current_data-2.5)*0.070*((Exp_Data[channel[:-1]+'T']+273.15)*(99.6*abs(current_data-2.5)))**0.5
							current_data_2 = np.sign(current_data_2-2.5)*0.070*((Exp_Data_2[channel[:-1]+'T']+273.15)*(99.6*abs(current_data_2-2.5)))**0.5
							plt.ylabel('Velocity (m/s)', fontsize=16)
							axis_scale = 'Y Scale BDP'
							secondary_axis_label = 'Velocity (mph)'
							secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) * 2.23694

						# Set parameters for heat flux plots
						if channel_list['Type'][channel] == 'Heat Flux':
							Data_Time = Time
							Data_Time_2 = Time_2
							# Set data to include slope and intercept
							current_data = current_data * scale_factor + offset
							current_data_2 = current_data_2 * scale_factor_2 + offset
							plt.ylabel('Heat Flux (kW/m$^2$)', fontsize = 16)
							axis_scale = 'Y Scale Heat Flux'

						# Set parameters for gas plots
						if channel_list['Type'][channel] == 'Gas':
							Data_Time = [t+float(channel_list[Transport_Time][channel])/60.0 for t in Time]
							Data_Time_2 = [t+float(channel_list[Transport_Time_2][channel])/60.0 for t in Time_2]
							# Set data to include slope and intercept
							current_data = current_data * scale_factor + offset
							current_data_2 = current_data_2 * scale_factor_2 + offset
							plt.ylabel('Gas Concentration (%)', fontsize = 16)
							axis_scale = 'Y Scale Gas'

						if channel_list['Type'][channel] == 'Carbon Monoxide':
							Data_Time = [t+float(channel_list[Transport_Time][channel])/60.0 for t in Time]
							Data_Time_2 = [t+float(channel_list[Transport_Time_2][channel])/60.0 for t in Time_2]
							# Set data to include slope and intercept
							current_data = current_data * scale_factor + offset
							current_data_2 = current_data_2 * scale_factor_2 + offset
							plt.ylabel('Gas Concentration (PPM)', fontsize = 16)
							axis_scale = 'Y Scale Carbon Monoxide'

						# Plot channel data 
						plt.plot(Data_Time, current_data, lw=1.25, marker=next(plot_markers), markevery=int(End_Time*60/mark_freq), mew=1.5,	mec='none', ms=6, label=channel+' Exp '+Exp_Num[11:])
						plt.plot(Data_Time_2, current_data_2, lw=1.25, marker=next(plot_markers), markevery=int(End_Time*60/mark_freq), mew=1.5,	mec='none',	ms=6, label=channel+' Exp '+str(comps[nn]), ls = '--')

					# Scale y-axis limit based on specified range in test description file
					if axis_scale == 'Y Scale BDP':
						plt.ylim([-np.float(Exp_Des[axis_scale][Test_Name]), np.float(Exp_Des[axis_scale][Test_Name])])
					else:
						plt.ylim([0, np.float(Exp_Des[axis_scale][Test_Name])])

					# Set axis options, legend, tickmarks, etc.
					ax1 = plt.gca()
					handles1, labels1 = ax1.get_legend_handles_labels()
					plt.xlim([0, End_Time])
					ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
					ax1_xlims = ax1.axis()[0:2]
					plt.grid(True)
					plt.xlabel('Time (min)', fontsize=16)
					plt.xticks(fontsize=16)
					plt.yticks(fontsize=16)
					# Secondary y-axis parameters
					if secondary_axis_label:
						ax2 = ax1.twinx()
						ax2.set_ylabel(secondary_axis_label, fontsize=20)
						plt.xticks(fontsize=16)
						plt.yticks(fontsize=16)
						if axis_scale == 'Y Scale BDP':
							ax2.set_ylim([-secondary_axis_scale, secondary_axis_scale])
						else:
							ax2.set_ylim([0, secondary_axis_scale])
					try:
						ax3=ax1.twiny()
						ax3.set_xlim(0,End_Time)
						EventTime=list(range(len(Events.index.values)))

						for i in range(len(Events.index.values)):
							EventTime[i] = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%H:%M:%S')-Ignition).total_seconds()

							plt.axvline(EventTime[i],color='0',lw=1) 

						ax3.set_xticks(EventTime)
						plt.setp(plt.xticks()[1], rotation=80)
						ax3.set_xticklabels(Events.index.values, fontsize=8, ha='left')
						fig.set_size_inches(20, 16)
					except:
						pass

					plt.legend(handles1, labels1, loc='upper left', fontsize=8, handlelength=3)
					plt.tight_layout()

					# Save plot to file
					plt.savefig(output_location + group + '.pdf')
					plt.close('all')
			except:
				pass