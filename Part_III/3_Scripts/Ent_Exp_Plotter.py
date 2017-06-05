###################################################################
# Script generates pressure/BDP plots for entrainment experiments #
###################################################################
import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt, savgol_filter
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

# Set file locations

data_location = '../0_Data/Ent_Experiment_Data/CSV/'

channel_location = '../1_Info/Ent/'

chart_location = '../1_Info/Ent/'

output_location_init = '../2_Plots/Ent_Experiment_Plots/'

info_file = '../1_Info/Ent/Description_of_Experiments.csv'

# Read in channel list
channel_list = pd.read_csv(channel_location+'Channels_List.csv')

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

		if Exp_Num != 'Experiment_1':
			continue

		# Set output location for results
		# output_location = output_location_init + Test_Name + '/'
		output_location = output_location_init

		# # If the folder exists delete it.
		# if os.path.exists(output_location):
		# 	shutil.rmtree(output_location)

		# If the folder doesn't exist create it.
		if not os.path.exists(output_location):
			os.makedirs(output_location)

		# Read in each experiment event file
		Events = pd.read_csv(channel_location + '/Events/' + Test_Name[:-4] + 'Events.csv')

		# Set index of experiment events files to Event
		Events = Events.set_index('Event')

		print ()
		print (Test_Name)
		
		#Set time to elapsed time column in experimental data.
		Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
		mark_freq = 15

		# Pull ignition time from events csv file
		Background = datetime.datetime.strptime(Events['Elapsed_Time']['Background'], '%H:%M:%S')

		# Adjust time for ignition offset
		Time = [((t - Background).total_seconds())/60 for t in Time]

		# Get End of Experiment Time
		End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%Y-%m-%d-%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Background'], '%Y-%m-%d-%H:%M:%S')).total_seconds()/60

		# Begin plotting
		for group in channel_groups.groups:
			# Skip excluded groups listed in test description file
			# if any([substring in group for substring in Exp_Des['Excluded Groups'][Test_Name].split('|')]):
			# 	continue

            #Create figure
			fig = plt.figure()

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

			# Plot style - cycle through 20 color pallet and define markers to cycle through
			plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
			plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

			# Print 'Plotting Chart XX'
			print ('Plotting ' + group.replace('_',' '))

			# Begin cycling through channels
			for channel in channel_groups.get_group(group).index.values:

				# Skip plot quantity if channel name is blank
				if pd.isnull(channel):
					continue

                # Skip excluded channels listed in test description file
				# if any([substring in channel for substring in Exp_Des['Excluded Channels'][Test_Name].split('|')]):
				# 	continue

                # Set scale factor and offset
				scale_factor = channel_list['ScaleFactor'][channel]
				offset = channel_list['Offset'][channel]
				current_data = Exp_Data[channel]

				# Set secondary axis default to None, unless otherwise stated below
				secondary_axis_label = None

                # Set parameters for velocity plots

                # If statement to find velocity type in channels csv
				if channel_list['Type'][channel] == 'BDP_Velocity':
					Data_Time = Time
					# Define cutoff and fs for filtering that
					cutoff = 50
					fs = 700
					current_data = current_data - np.average(current_data[:90])
					current_data = butter_lowpass_filtfilt(current_data, cutoff, fs)
					# current_data = savgol_filter(current_data,11,3)
					# current_data = current_data.rolling(window=5, center=True).mean()
					# Calculate result
					# current_data = (np.sign(current_data)*0.070*((Exp_Data[channel[:-1]+'T']+273.15)*(9.96*abs(current_data)))**0.5) * 2.23694
					current_data = (np.sign(current_data)*0.070*((255.)*(9.96*abs(current_data)))**0.5) * 2.23694
					plt.ylabel('Velocity (mph)', fontsize=28)
					line_style = '-'
					axis_scale = 'Y Scale BDP'
					secondary_axis_label = 'Velocity (m/s)'
					secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) / 2.23694

				# Set parameters for pressure plots

                # If statement to find pressure type in channels csv
				if channel_list['Type'][channel] == 'Pressure':
					Data_Time = Time
					cutoff = 50
					fs = 700
					current_data = scale_factor * current_data + offset 
					current_data = current_data - np.average(current_data[:90])
					current_data = butter_lowpass_filtfilt(current_data, cutoff, fs)
					plt.ylabel('Pressure (Pa)', fontsize=28)
					line_style = '-'
					axis_scale = 'Y Scale PRESSURE'
					secondary_axis_label = 'Pressure (psi)'
					secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) * 0.000145038

				# Plot channel data or save channel data for later usage, depending on plot mode
				plt.plot(Data_Time,
					current_data,
					lw=1.5,
					marker=next(plot_markers),
					markevery=int(End_Time*60/mark_freq),
					mew=3,
					mec='none',
					ms=7,
					label=channel_list['Title'][channel],
					linewidth=1.5)

				# Scale y-axis limit based on specified range in test description file
				if axis_scale == 'Y Scale BDP' or axis_scale == 'Y Scale PRESSURE':
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
				plt.xlabel('Time (min)', fontsize=32)
				plt.xticks(fontsize=28)
				plt.yticks(fontsize=28)

			# Secondary y-axis parameters
			if secondary_axis_label:
				ax2 = ax1.twinx()
				ax2.set_ylabel(secondary_axis_label, fontsize=32)
				plt.xticks(fontsize=28)
				plt.yticks(fontsize=28)
				if axis_scale == 'Y Scale BDP':
					ax2.set_ylim([-secondary_axis_scale, secondary_axis_scale])
				else:
					ax2.set_ylim([0, secondary_axis_scale])

			try:
				ax3=ax1.twiny()
				ax3.set_xlim(0,End_Time)
				EventTime=list(range(len(Events.index.values)))

				for i in range(len(Events.index.values)):
					EventTime[i] = (datetime.datetime.strptime(Events['Elapsed_Time'][i], '%H:%M:%S')-Background).total_seconds()

					plt.axvline(EventTime[i],color='0',lw=2) 

				ax3.set_xticks(EventTime)
				plt.setp(plt.xticks()[1], rotation=67.5)		
				ax3.set_xticklabels(Events.index.values, fontsize=18, ha='left')
				fig.set_size_inches(20, 16)
				plt.tight_layout()

			except:
				pass

			plt.legend(handles1, labels1, loc='upper left', fontsize=24, handlelength=3)

            # Save plot to file
			plt.savefig(output_location+Exp_Num+'_'+group+'.jpg')
			plt.close('all')
	exit()
   