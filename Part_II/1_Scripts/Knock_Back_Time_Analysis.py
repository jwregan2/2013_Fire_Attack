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

# Set file locations

data_location = '../2_Data/Smaller_Data/'

channel_location = '../3_Info/'

chart_location = '../3_Info/'

output_location_init = '../0_Images/Results/'

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

# Create numpy array containing desired experiment sets to compare; 
# 	each array corresponds to a comparison set
comparison_sets = np.array([ [2,7,13],
							 [6,8,14],
							 [11,16],
							 [18,20,22,24] ])
#,[22,24] ])

# Create an array of row numbers corresponding to suppression 
# 	event(s) of interest for each experiment in each set
# event_row_nums = np.array([ [5,5,5],
# 							[5,5,5], 
# 							[5,5,5],
# 							[2,2,2,2] ])
#							,[ [2,6],[2,3,6] ] ])

event_row_nums = [5,5,5,2]

# Create numpy array with sensors to be used for analysis of each 
# 	comparison set (i.e., each array in comparison_sets)
sensor_groups = np.array([ ['End_Hall_Temps','Middle_Hall_Temps','Victim_1_Temps','Victim_3_Temps'],
						   ['End_Hall_Temps','Middle_Hall_Temps','Victim_1_Temps'], 
						   ['End_Hall_Temps','Middle_Hall_Temps','Start of Hall','Victim_1_Temps','Victim_3_Temps'],
						   ['Bedroom_1_Temps'] ])

# Loop through experiments in each comparison set
set_num = 0
for Exp_Set in comparison_sets:
	extinguish_event_index = event_row_nums[set_num]-1
	print('--- Comparing Experiments from set',Exp_Set,' ---')
	knock_back_time_df = pd.DataFrame(sensor_groups[set_num],columns=['Sensor Group'])
	for Exp_Num in Exp_Set:
		# Define experiment number, test name, and data file name
		Exp_Num = str(Exp_Num)
		Test_Name = 'Experiment_'+Exp_Num
		File_Name = Test_Name+'_Data'

		# Read in experimental data
		Exp_Data = pd.read_csv(data_location+File_Name+'.csv')

		# # Set output location for results
		# output_location = output_location_init + Test_Name + '/'

		# # Create directory if it doesn't already exist
		# if not os.path.exists(output_location):
		# 	os.makedirs(output_location)

		# Get house & data speed
		House = Exp_Des.loc[File_Name, 'House']
		Speed = Exp_Des.loc[File_Name, 'Speed']

		# Read in event file for given test and set event column as index
		Events = pd.read_csv(channel_location+'Events/'+Test_Name+'_Events.csv', index_col='Event')

		print(' Loaded data and event files for '+Test_Name)

		extinguish_time = Events['Time'].iloc[extinguish_event_index]

		# If statements to determine whether or not data is in high speed and assigning time accordingly based on data csv
		if Speed == 'low':
			#Set time to elapsed time column in experimental data.
			Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
			mark_freq = 15
			extinguish_index = Exp_Data[Exp_Data['Elapsed Time']==extinguish_time].index.tolist()[0]
			nth_row = 1
		elif Speed == 'high':
			#Set time to elapsed time column in experimental data.
			Time = [datetime.datetime.strptime(t, '%M:%S.%f') for t in Exp_Data['Elapsed Time']]
			mark_freq = 5
			nth_row = 10
			extinguish_index = Exp_Data[Exp_Data['Elapsed Time']==extinguish_time[2:]+'.0'].index.tolist()[0]
		else:
			print('[ERROR!]: data speed not set properly!')
			print(' 	Speed = '+Speed)
			exit()

		# Pull ignition time from events dataframe & adjust time accordingly
		Ignition = datetime.datetime.strptime(Events.loc['Ignition', 'Time'], '%H:%M:%S')
		Time = [((t - Ignition).total_seconds())/60 for t in Time]

		# Get end time for given test
		End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60

		if House == 'a':
			scalefactor = 'ScaleFactor_A'
			Transport_Time = 'Transport_Time_A'
		elif House == 'b':
			scalefactor = 'ScaleFactor_B'
			Transport_Time = 'Transport_Time_B'
		else:
			print('[ERROR!]: House label not set properly!')
			print(' 	House = '+House)
			exit()

		delta_T_col = []
		knock_back_time_col = []
		for group in sensor_groups[set_num]:
			channel_names = channel_groups.get_group(group).index.values
			group_data = Exp_Data[channel_names][extinguish_index-nth_row+1:]
			initial_temps = np.mean(group_data[:].iloc[:nth_row])		
			count = 0
			entireloop = True
			for index,row in group_data.iterrows():
				count = count + 1
				if count != nth_row:
					continue
				else:
					count = 0
					sec_values = np.mean(group_data[:].loc[-nth_row+1+index:index])
					max_T = max(sec_values)
					min_T = min(sec_values)
					if (max_T-min_T) < 30 and max_T < 100:
						avg_next_5s = np.mean(group_data[:].iloc[index-extinguish_index:index-extinguish_index+5*nth_row])
						max_avg = max(avg_next_5s)
						min_avg = min(avg_next_5s)
						if max_avg-min_avg < 30:
							delta_Ts = initial_temps-sec_values
							delta_T_col.append(max(delta_Ts)) 
							knock_back_time_col.append((index-extinguish_index)/nth_row)
							entireloop = False						
							break
			
			if entireloop:
				delta_T_col.append(100000)
				knock_back_time_col.append(100000)

		knock_back_time_df['Exp. '+Exp_Num+' Delta T'] = delta_T_col
		knock_back_time_df['Exp. '+Exp_Num+' Knock Back Time'] = knock_back_time_col

	knock_back_time_df = knock_back_time_df.set_index('Sensor Group')
	print(knock_back_time_df)
	exit()
	set_num = set_num+1

	# # Begin plotting
	# for group in channel_groups.groups:
	# 	# Skip excluded groups listed in test description file
	# 	if any([substring in group for substring in Exp_Des['Excluded Groups'][Test_Name].split('|')]):
	# 		continue

 #        #Create figure
	# 	fig = plt.figure()

 #        # Define 20 color pallet using RGB values
	# 	tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
	# 	(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
	# 	(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
	# 	(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
	# 	(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
		
	# 	# Define RGB values in pallet 
	# 	for i in range(len(tableau20)):
	# 			r, g, b = tableau20[i]
	# 			tableau20[i] = (r / 255., g / 255., b / 255.)

	# 	# Plot style - cycle through 20 color pallet and define markers to cycle through
	# 	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	# 	plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	# 	# Print 'Plotting Chart XX'
	# 	print ('Plotting ' + group.replace('_',' '))

	# 	# Begin cycling through channels
	# 	for channel in channel_groups.get_group(group).index.values:

	# 		# Skip plot quantity if channel name is blank
	# 		if pd.isnull(channel):
	# 			continue

 #            # Skip excluded channels listed in test description file
	# 		if any([substring in channel for substring in Exp_Des['Excluded Channels'][Test_Name].split('|')]):
	# 			continue

 #            # Set scale factor and offset
	# 		scale_factor = channel_list[scalefactor][channel]
	# 		offset = channel_list['Offset'][channel]
	# 		current_data = Exp_Data[channel]

	# 		# Set secondary axis default to None, unless otherwise stated below
	# 		secondary_axis_label = None

	# 		# Set parameters for temperature plots

	# 		# If statement to find temperature type in channels csv
	# 		if channel_list['Type'][channel] == 'Temperature':
	# 			Data_Time = Time
	# 			# Set data to include slope and intercept
	# 			current_data = current_data * scale_factor + offset
	# 			# Set y-label to degrees F with LaTeX syntax
	# 			plt.ylabel('Temperature ($^\circ$F)', fontsize = 32)
	# 			# Search for skin inside description of events file for scaling
	# 			if 'Skin' in group:
	# 				axis_scale = 'Y Scale Skin Temperature'
	# 			else: # Default to standard temperature scale
	# 				axis_scale = 'Y Scale Temperature'
	# 			# Set secondary y-axis label to degrees C
	# 			secondary_axis_label = 'Temperature ($^\circ$C)'
	# 			#Set scaling dependent on axis scale defined above
	# 			secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) * 5/9 - 32

 #            # Set parameters for velocity plots

 #            # If statement to find velocity type in channels csv
	# 		if channel_list['Type'][channel] == 'Velocity':
	# 			Data_Time = Time
	# 			# Define cutoff and fs for filtering 
	# 			cutoff = 50
	# 			fs = 700
	# 			current_data = current_data - np.average(current_data[:90]) + 2.5
	# 			current_data = butter_lowpass_filtfilt(current_data, cutoff, fs)
	# 			#Calculate result
	# 			current_data = (np.sign(current_data-2.5)*0.070*((Exp_Data[channel[:-1]+'T']+273.15)*(99.6*abs(current_data-2.5)))**0.5) * 2.23694
	# 			plt.ylabel('Velocity (mph)', fontsize=28)
	# 			line_style = '-'
	# 			axis_scale = 'Y Scale BDP'
	# 			secondary_axis_label = 'Velocity (m/s)'
	# 			secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) / 2.23694

 #            # Set parameters for heat flux plots

	# 		# If statement to find heat flux type in channels csv
	# 		if channel_list['Type'][channel] == 'Wall Heat Flux':
	# 			Data_Time = Time
	# 			# Set data to include slope and intercept
	# 			current_data = current_data * scale_factor + offset
	# 			plt.ylabel('Heat Flux (kW/m$^2$)', fontsize = 32)
	# 			axis_scale = 'Y Scale Wall Heat Flux'

	# 		if channel_list['Type'][channel] == 'Floor Heat Flux':
	# 			Data_Time = Time
	# 			# Set data to include slope and intercept
	# 			current_data = current_data * scale_factor + offset
	# 			plt.ylabel('Heat Flux (kW/m$^2$)', fontsize = 32)
	# 			axis_scale = 'Y Scale Floor Heat Flux'

	# 		if channel_list['Type'][channel] == 'Victim Heat Flux':
	# 			Data_Time = Time
	# 			# Set data to include slope and intercept
	# 			current_data = current_data * scale_factor + offset
	# 			plt.ylabel('Heat Flux (kW/m$^2$)', fontsize = 32)
	# 			axis_scale = 'Y Scale Victim Heat Flux'

	# 		# Set parameters for gas plots

	# 		# If statement to find gas type in channels csv
	# 		if channel_list['Type'][channel] == 'Gas':
	# 			Data_Time = [t+float(channel_list[Transport_Time][channel])/60.0 for t in Time]
	# 			# Set data to include slope and intercept
	# 			current_data = current_data * scale_factor + offset
	# 			plt.ylabel('Gas Concentration (%)', fontsize = 32)
	# 			axis_scale = 'Y Scale Gas'

	# 		# If statement to find gas type in channels csv
	# 		if channel_list['Type'][channel] == 'Carbon Monoxide':
	# 			Data_Time = [t+float(channel_list[Transport_Time][channel])/60.0 for t in Time]
	# 			# Set data to include slope and intercept
	# 			current_data = current_data * scale_factor + offset
	# 			plt.ylabel('Gas Concentration (PPM)', fontsize = 32)
	# 			axis_scale = 'Y Scale Carbon Monoxide'

	# 		# Plot channel data or save channel data for later usage, depending on plot mode
	# 		plt.plot(Data_Time,
	# 			current_data,
	# 			lw=1.5,
	# 			marker=next(plot_markers),
	# 			markevery=int(End_Time*60/mark_freq),
	# 			mew=3,
	# 			mec='none',
	# 			ms=7,
	# 			label=channel_list['Title'][channel])

	# 		# Scale y-axis limit based on specified range in test description file
	# 		if axis_scale == 'Y Scale BDP':
	# 			plt.ylim([-np.float(Exp_Des[axis_scale][Test_Name]), np.float(Exp_Des[axis_scale][Test_Name])])
	# 		else:
	# 			plt.ylim([0, np.float(Exp_Des[axis_scale][Test_Name])])

 #            # Set axis options, legend, tickmarks, etc.
	# 		ax1 = plt.gca()
	# 		handles1, labels1 = ax1.get_legend_handles_labels()
	# 		plt.xlim([0, End_Time])
	# 		ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
	# 		ax1_xlims = ax1.axis()[0:2]
	# 		plt.grid(True)
	# 		plt.xlabel('Time (min)', fontsize=32)
	# 		plt.xticks(fontsize=28)
	# 		plt.yticks(fontsize=28)

	# 	# Secondary y-axis parameters
	# 	if secondary_axis_label:
	# 		ax2 = ax1.twinx()
	# 		ax2.set_ylabel(secondary_axis_label, fontsize=32)
	# 		plt.xticks(fontsize=28)
	# 		plt.yticks(fontsize=28)
	# 		if axis_scale == 'Y Scale BDP':
	# 			ax2.set_ylim([-secondary_axis_scale, secondary_axis_scale])
	# 		else:
	# 			ax2.set_ylim([0, secondary_axis_scale])

	# 	try:
	# 		ax3=ax1.twiny()
	# 		ax3.set_xlim(0,End_Time)
	# 		EventTime=list(range(len(Events.index.values)))

	# 		for i in range(len(Events.index.values)):
	# 			EventTime[i] = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%H:%M:%S')-Ignition).total_seconds()

	# 			plt.axvline(EventTime[i],color='0',lw=2) 

	# 		ax3.set_xticks(EventTime)
	# 		plt.setp(plt.xticks()[1], rotation=67.5)		
	# 		ax3.set_xticklabels(Events.index.values, fontsize=18, ha='left')
	# 		fig.set_size_inches(20, 16)
	# 		plt.tight_layout()
 #            # # Add vertical lines and labels for timing information (if available)
 #            # ax3 = ax1.twiny()
 #            # ax3.set_xlim(ax1_xlims)
 #            # # Remove NaN items from event timeline
 #            # events = all_times[test_name].dropna()
 #            # # Ignore events that are commented starting with a pound sign
 #            # events = events[~events.str.startswith('#')]
 #            # [plt.axvline(_x - start_of_test, color='0.50', lw=1) for _x in events.index.values]
 #            # ax3.set_xticks(events.index.values - start_of_test)
 #            # plt.setp(plt.xticks()[1], rotation=60)
 #            # ax3.set_xticklabels(events.values, fontsize=8, ha='left')
 #            # plt.xlim([0, end_of_test - start_of_test])
 #            # # Increase figure size for plot labels at top
 #            # fig.set_size_inches(10, 6)
	# 	except:
	# 		pass

	# 	plt.legend(handles1, labels1, loc='upper left', fontsize=24, handlelength=3)

 #        # Save plot to file
	# 	plt.savefig(output_location + group + '.png')
	# 	plt.close('all')
   