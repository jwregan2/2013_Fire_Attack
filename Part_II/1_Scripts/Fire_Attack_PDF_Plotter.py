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
import pickle 
from natsort import natsorted

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
data_location_gas_cooling = '../2_Data/'

channel_location = '../3_Info/'

chart_location = '../3_Info/'

output_location_init = '../0_Images/Script_Figures/Results/'

info_location = '../3_Info/'

info_file = '../3_Info/Description_of_Experiments.csv'

transport_times = pd.read_csv('../3_Info/Updated_Transport_Times.csv').set_index('Experiment')

# Read in channel list
channel_list = pd.read_csv(channel_location+'Channels.csv')

# Set index value for channels as 'Channel'
channel_list = channel_list.set_index('Channel')

# Create groups data by grouping channels for 'Chart'
channel_groups = channel_list.groupby('Primary_Chart')
# channel_groups = channel_list.groupby('Secondary_Chart')

#List of Channels for Experiment 25, Gas Cooling Plots
all_gas_channels = pd.read_csv(info_location + 'Gas_Channels.csv').set_index('Channel')

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)

# Set index of description of experiments to Experiment
Exp_Des = Exp_Des.set_index('Experiment')

# Set files to skip in experimental directory
skip_files = ['example']

all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))

event_label_size = 7
axis_title_size = 8
tic_label_size = 7
legend_font_size = 6


# **************************************************************************************
# ************** Define 20 Color Pallet for Plots and set as RGB Values ****************
# **************************************************************************************

tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Define RGB values in pallet 
for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b / 255.)

# # Loop through Experiment files
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

		# Set output location for results
		if Test_Name == 'Experiment_27_Data':
			output_location = output_location_init + 'Experiment_26_Data' + '/'
		else:
			output_location = output_location_init + Test_Name + '/'

		# # If the folder exists delete it.
		# if os.path.exists(output_location):
		# 	shutil.rmtree(output_location)

		# If the folder doesn't exist create it.
		if not os.path.exists(output_location):
			os.makedirs(output_location)

		# Get which house from description of events file
		House = Exp_Des['House'][Test_Name]

		# Get which data speed from description of events file
		Speed = Exp_Des['Speed'][Test_Name]

		# Read in each experiment event file
		Events = pd.read_csv(channel_location + '/Events/' + Test_Name[:-4] + 'Events.csv')

		# Set index of experiment events files to Event
		Events = Events.set_index('Event')

		print ()
		print (Test_Name)
		 
		# If statements to determine whether or not data is in high speed and assigning time accordingly based on data csv
		if Speed == 'low':
			#Set time to elapsed time column in experimental data.
			Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
			mark_freq = 8

		if Speed == 'high':
			#Set time to elapsed time column in experimental data.
			Time = [datetime.datetime.strptime(t, '%M:%S.%f') for t in Exp_Data['Elapsed Time']]
			mark_freq = 3

		# Pull ignition time from events csv file
		Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

		# Adjust time for ignition offset
		Time = [((t - Ignition).total_seconds())/60 for t in Time]

		#Get End of Experiment Time
		End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60
		
		if House == 'a':
			scalefactor = 'ScaleFactor_A'
			Transport_Time = 'Transport_Time_A'

		if House == 'b':
			scalefactor = 'ScaleFactor_B'
			Transport_Time = 'Transport_Time_B'

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
			print ('Plotting ' + group.replace('_',' '))

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
				offset = channel_list['Offset'][channel]
				current_data = Exp_Data[channel]

				# Set secondary axis default to None, unless otherwise stated below
				secondary_axis_label = None

				# Set parameters for temperature plots

				# If statement to find temperature type in channels csv
				if channel_list['Type'][channel] == 'Temperature':
					Data_Time = Time
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					# Set y-label to degrees F with LaTeX syntax
					plt.ylabel('Temperature ($^\circ$F)', fontsize = axis_title_size)
					# Search for skin inside description of events file for scaling
					if 'Skin' in group:
						axis_scale = 'Y Scale Skin Temperature'
					else: # Default to standard temperature scale
						axis_scale = 'Y Scale Temperature'
					# Set secondary y-axis label to degrees C
					secondary_axis_label = 'Temperature ($^\circ$C)'
					#Set scaling dependent on axis scale defined above
					secondary_axis_scale = (np.float(Exp_Des[axis_scale][Test_Name]) - 32) * (5/9)

                # Set parameters for velocity plots

                # If statement to find velocity type in channels csv
				if channel_list['Type'][channel] == 'Velocity':
					Data_Time = Time
					# Define cutoff and fs for filtering 
					cutoff = 50
					fs = 700
					current_data = current_data - np.average(current_data[:90]) + 2.5
					current_data = butter_lowpass_filtfilt(current_data, cutoff, fs)
					#Calculate result
					current_data = (np.sign(current_data-2.5)*0.070*((Exp_Data[channel[:-1]+'T']+273.15)*(99.6*abs(current_data-2.5)))**0.5) * 2.23694
					plt.ylabel('Velocity (mph)', fontsize=axis_title_size)
					line_style = '-'
					axis_scale = 'Y Scale BDP'
					secondary_axis_label = 'Velocity (m/s)'
					secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) / 2.23694

                # Set parameters for heat flux plots

				# If statement to find heat flux type in channels csv
				if channel_list['Type'][channel] == 'Wall Heat Flux':
					Data_Time = Time
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					plt.ylabel('Heat Flux (kW/m$^2$)', fontsize = axis_title_size)
					axis_scale = 'Y Scale Wall Heat Flux'

				if channel_list['Type'][channel] == 'Floor Heat Flux':
					Data_Time = Time
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					plt.ylabel('Heat Flux (kW/m$^2$)', fontsize = axis_title_size)
					axis_scale = 'Y Scale Floor Heat Flux'

				if channel_list['Type'][channel] == 'Victim Heat Flux':
					Data_Time = Time
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					plt.ylabel('Heat Flux (kW/m$^2$)', fontsize = axis_title_size)
					axis_scale = 'Y Scale Victim Heat Flux'

				# Set parameters for gas plots

				# If statement to find gas type in channels csv
				if channel_list['Type'][channel] == 'Gas':
					updated_transport = transport_times['Victim_' + channel[0] + '_' + str(House.upper())][Test_Name]
					Data_Time = [t-float(updated_transport)/60.0 for t in Time]
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					plt.ylabel('Gas Concentration (%)', fontsize = axis_title_size)
					axis_scale = 'Y Scale Gas'

				# If statement to find gas type in channels csv
				if channel_list['Type'][channel] == 'Carbon Monoxide':
					updated_transport = transport_times['Victim_' + channel[0] + '_' + str(House.upper())][Test_Name]
					Data_Time = [t-float(updated_transport)/60.0 for t in Time]
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					plt.ylabel('Gas Concentration (PPM)', fontsize = axis_title_size)
					axis_scale = 'Y Scale Carbon Monoxide'

				# If statement to find pressure type in channels csv
				if channel_list['Type'][channel] == 'Pressure':
					Data_Time = Time

					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					current_data = current_data - np.average(current_data[0:60])

					# Set y-label to degrees F with LaTeX syntax
					plt.ylabel('Pressure (Pa)', fontsize = axis_title_size)
					# Search for skin inside description of events file for scaling
					axis_scale = 'Y Scale Pressure'

				# Plot channel data or save channel data for later usage, depending on plot mode
				plt.plot(Data_Time,
					current_data,
					lw=1,
					marker=next(plot_markers),
					markevery=int(End_Time*60/mark_freq),
					mew=3,
					mec='none',
					ms=3,
					label=channel_list['Title'][channel])

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
				plt.xlabel('Time (min)', fontsize=axis_title_size)
				plt.xticks(fontsize=tic_label_size)
				plt.yticks(fontsize=tic_label_size)

			# Secondary y-axis parameters
			if secondary_axis_label:
				ax2 = ax1.twinx()
				ax2.set_ylabel(secondary_axis_label, fontsize=axis_title_size)
				plt.xticks(fontsize=tic_label_size)
				plt.yticks(fontsize=tic_label_size)
				if axis_scale == 'Y Scale BDP':
					ax2.set_ylim([-secondary_axis_scale, secondary_axis_scale])
				elif axis_scale == 'Y Scale Temperature':
					ax2.set_ylim([-17.78, secondary_axis_scale])
				else:
					ax2.set_ylim([0, secondary_axis_scale])

			try:
				ax3=ax1.twiny()
				ax3.set_xlim(0,End_Time)

				i = 0

				EventTime = np.empty(len(Events['Results_Time'].dropna().index.values))
				EventTime[:] = nan
				EventLabel = ['']*len(Events['Results_Time'].dropna().index.values)

				for e in Events['Results_Time'].dropna().index.values:
					# print (e)
					EventTime[i] = (datetime.datetime.strptime(Events['Results_Time'][e], '%H:%M:%S')-Ignition).total_seconds()
					EventLabel[i] = e
					plt.axvline(EventTime[i],color='0',lw=1.5) 
					i = i + 1
				
				ax3.set_xticks(EventTime)
				plt.setp(plt.xticks()[1], rotation=67.5)		
				ax3.set_xticklabels(EventLabel, fontsize=event_label_size, ha='left')
				fig.set_size_inches(5, 4)
				plt.tight_layout()
			except:
				print('Error Setting Secondary Axis')
				pass

			plt.legend(handles1, labels1, loc='upper left', fontsize=legend_font_size, handlelength=2)

			# Save plot to file
			plt.savefig(output_location + group + '.pdf')
			plt.close('all')

print ('-------------------------------------- Plotting Gas Cooling Results Charts ----------------------------------')

# Set Channels for Gas Cooling.
gas_cooling_plots = pd.DataFrame({'1TC':['1TC7','1TC6','1TC5','1TC4','1TC3','1TC2','1TC1'],
						   		 '2TC':['3TC7','3TC6','3TC5','3TC4','3TC3','3TC2','3TC1'],
						   		 '3TC':['7TC7','7TC6','7TC5','7TC4','7TC3','7TC2','7TC1'],
						   		 '4TC':['8TC7','8TC6','8TC5','8TC4','8TC3','8TC2','8TC1']})

exp = 'Experiment_25_Data'

all_exp_data = pickle.load(open(data_location_gas_cooling + 'all_exp_data.dict', 'rb'))

data = all_exp_data[exp]

all_flow_data = pickle.load(open(data_location_gas_cooling + 'all_flow_data.dict', 'rb'))

#Set output 
output_location = output_location_init + exp + '/'

# If the folder doesn't exist create it.
if not os.path.exists(output_location):
	os.makedirs(output_location)

for plot in gas_cooling_plots.columns:
	
	print('Plotting '+ plot)
	
		
	#Create figure
	fig = plt.figure()
	fig.set_size_inches(5, 4)

	# Plot style - cycle through 20 color pallet and define markers to cycle through
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	if plot == '1TC':
		y_max = 2000
	else:
		y_max = 800

	ax1 = plt.gca()
	ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
	ax1_xlims = ax1.axis()[0:2]
	plt.ylim([0, y_max]) #Exp_Des['Y Scale Temperature'][exp]])
	plt.ylabel('Temperature ($^\circ$F)', fontsize=48)
	plt.grid(True)
	plt.xlabel('Time (seconds)', fontsize=48)
	plt.xticks(fontsize=44)
	plt.yticks(fontsize=44)

	for channel in gas_cooling_plots[plot]:

		channel_label = all_gas_channels['Title'][channel]

		ax1.plot(data[channel].index/60, data[channel], lw = 4, marker=next(plot_markers), markevery=500,
							label = channel_label, markersize=15 )

	h1, l1 = ax1.get_legend_handles_labels()
	ax1.legend(h1, l1, bbox_to_anchor=(1.35, 0.20), loc='lower right', fontsize=40, handlelength=2, labelspacing=.15)

	ax3=ax1.twiny()

	i = 0

	EventTime = np.empty(len(all_exp_events[exp[:-4]+'Events']['Flow_Time'].dropna().index))
	EventTime[:] = nan
	EventLabel = ['']*len(all_exp_events[exp[:-4]+'Events']['Flow_Time'].dropna().index)

	for e in all_exp_events[exp[:-4]+'Events']['Flow_Time'].dropna().index:
		EventTime[i] = all_exp_events[exp[:-4]+'Events']['Flow_Time'][e]/60
		EventLabel[i] = e
		plt.axvline(EventTime[i],color='0',lw=2) 
		i = i + 1
	
	ax3.set_xticks(EventTime)
	plt.setp(plt.xticks()[1], rotation=67.5)		
	ax3.set_xticklabels(EventLabel, fontsize=28, ha='left')	


	plt.subplots_adjust(top=0.60, right=0.78)

	
	ax1.tick_params(axis='x', which='major', pad=15)

	fig.set_size_inches(5, 4)

	ax3.set_xlim(0,5)
	ax1.set_xlim(0,5)

	plt.savefig(output_location + plot + '_0min_to_5min.pdf')
	ax3.set_xlim(5,12)
	ax1.set_xlim(5,12)

	plt.savefig(output_location + plot + '_5min_to_12min.pdf')
	ax3.set_xlim(12,all_exp_events[exp[:-4]+'Events']['Time_Seconds']['End Experiment']/60)
	ax1.set_xlim(12,all_exp_events[exp[:-4]+'Events']['Time_Seconds']['End Experiment']/60)

	plt.savefig(output_location + plot + '_12min_to_End.pdf')
	plt.close('all')

print ('-------------------------------------- Plotting Moisture Results Charts ----------------------------------')

data_location_moisture = '../2_Data/Laser/'

experiments = os.listdir(data_location_moisture)

exp_info = pd.read_csv(info_location + 'Moisture_Info.csv').set_index('Experiment')
exp_info_grouped = exp_info.groupby(['Vent', 'Location'])

all_laser_data = {}
low = pd.DataFrame()
high = pd.DataFrame()

for exp in natsorted(experiments):
	if exp.endswith('.csv'):
		print ('	Plotting ' + exp[:-4].replace('_', ' '))
		all_laser_data[exp[:-4]] = pd.read_csv(data_location_moisture + exp).set_index('Time')

		all_laser_data[exp[:-4]] = all_laser_data[exp[:-4]].replace(0.0, np.nan)

		# Create figure
		fig = plt.figure()
		fig.set_size_inches(5, 4)
		ax1 = plt.gca()
		ax1.set_xlim(0,all_exp_events[exp[:-4]+'_Events']['Results_Time_Seconds']['End Experiment']/60)

		plt.xticks(fontsize=28)
		plt.yticks(fontsize=28)
		plt.grid(True)

		# Plot style - cycle through 20 color pallet and define markers to cycle through
		plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
		plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

		ax1.plot(all_laser_data[exp[:-4]].index, all_laser_data[exp[:-4]].max(axis=1), label='Bedroom 4 Moisture', marker=next(plot_markers), markevery=10)

		ax3=ax1.twiny()
		

		ax3.set_xlim(0,all_exp_events[exp[:-4]+'_Events']['Results_Time_Seconds']['End Experiment']/60)

		i = 0

		EventTime = np.empty(len(all_exp_events[exp[:-4]+'_Events']['Results_Time'].dropna().index))
		EventTime[:] = nan
		EventLabel = ['']*len(all_exp_events[exp[:-4]+'_Events']['Results_Time'].dropna().index)

		for e in all_exp_events[exp[:-4]+'_Events']['Results_Time'].dropna().index:
			EventTime[i] = all_exp_events[exp[:-4]+'_Events']['Results_Time_Seconds'][e]/60
			EventLabel[i] = e
			plt.axvline(EventTime[i],color='0',lw=2) 
			i = i + 1
		
		ax3.set_xticks(EventTime)
		plt.setp(plt.xticks()[1], rotation=67.5)		
		ax3.set_xticklabels(EventLabel, fontsize=28, ha='left')	
		
		plt.ylim([0,12])
		ax1.set_yticks(np.arange(0, 12, 1))

		ax1.legend(fontsize=24, handlelength=2)
		plt.subplots_adjust(top=0.80)
		ax1.set_xlabel('Time (Minutes)', fontsize=38)
		ax1.set_ylabel('Moisture Content (\% Volume)', fontsize=38)
		plt.xticks(fontsize=28)
		plt.yticks(fontsize=28)
		plt.tight_layout()


		plt.savefig('../0_Images/Script_Figures/Results/' + exp[:-4] + '_Data/Bedroom_4_Moisture.pdf')

		plt.close('all')

print ('-------------------------------------- Plotting Necrosis Depth Results Charts ----------------------------------')

data_location_skin = '../2_Data/Skin_Temp_Data/'

experiments = os.listdir(data_location_skin)

for exp in natsorted(experiments):
	if exp.endswith('.csv'):
		print ('	Plotting ' + exp[:-4].replace('_', ' '))
		
		data = pd.read_csv(data_location_skin + exp).set_index('Time')
		exp = exp[:-4]

		if Exp_Des['Speed'][exp] == 'high':
			markers = 1000
		if Exp_Des['Speed'][exp] == 'low':
			markers = 10

		for vic in ['Vic 1', 'Vic 3']:
			
			# Create figure
			fig = plt.figure()
			
			x_min = 0
			x_max = all_exp_events[exp[:-5] +'_Events']['Results_Time_Seconds']['End Experiment']/60

			fig.set_size_inches(5, 4)
			ax1 = plt.gca()
			plt.xticks(fontsize=28)
			plt.yticks(fontsize=28)
			plt.grid(True)

			ax2 = ax1.twinx()

			ax1.set_xlim(x_min,x_max)
			ax2.set_ylim(0,10)

			ax2.set_xlim(x_min, x_max)
			ax2.set_ylim(0,1)
			ax2.tick_params(axis='x', top='off', labeltop='off')
			plt.yticks(fontsize=32)



			# Plot style - cycle through 20 color pallet and define markers to cycle through
			plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
			plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

			ax1.plot(data.index, data[vic + ' necrosis depth'], label='Necrosis Depth', marker='s', color=(31/255, 119/255, 180/255), markevery=markers )
			ax2.plot(data.index, data[vic + ', surface necrosis'], label='Surface Necrosis', marker='o', color=(174/255, 199/255, 232/255), markevery=markers )

			ax3=ax1.twiny()

			ax3.set_xlim(0,all_exp_events[exp[:-5] +'_Events']['Results_Time_Seconds']['End Experiment']/60)

			i = 0

			EventTime = np.empty(len(all_exp_events[exp[:-5] +'_Events']['Results_Time'].dropna().index))
			EventTime[:] = nan
			EventLabel = ['']*len(all_exp_events[exp[:-5] +'_Events']['Results_Time'].dropna().index)

			for e in all_exp_events[exp[:-5]+'_Events']['Results_Time'].dropna().index:
				EventTime[i] = all_exp_events[exp[:-5]+'_Events']['Results_Time_Seconds'][e]/60
				EventLabel[i] = e
				plt.axvline(EventTime[i],color='0',lw=2) 
				i = i + 1
			
			ax3.set_xticks(EventTime)
			plt.setp(plt.xticks()[1], rotation=67.5)		
			ax3.set_xticklabels(EventLabel, fontsize=28, ha='left')	
			
			plt.ylim([0,12])
			ax1.set_yticks(np.arange(0, 12, 1))

			h1, l1 = ax1.get_legend_handles_labels()
			h2, l2 = ax2.get_legend_handles_labels()
			ax1.legend(h1+h2, l1+l2, fontsize=32, handlelength=2, loc='upper left')

			ax1.set_xlabel('Time (Minutes)', fontsize=38)
			ax1.set_ylabel('Necrosis Depth (mm)', fontsize=38)
			ax2.set_ylabel('Surface Necrosis (Dimensionless)', fontsize=38)
			plt.xticks(fontsize=28)
			plt.yticks(fontsize=28)
			plt.tight_layout()

			plt.savefig('../0_Images/Script_Figures/Results/' + exp + '/' + vic.replace(' ', '_') + '_Necrosis_Depth.pdf')

			plt.close('all')