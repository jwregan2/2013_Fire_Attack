import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
import datetime
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle
from bokeh.charts import Scatter, output_file, show
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, output_file, show, save,ColumnDataSource,reset_output
from bokeh.models import HoverTool, Range1d, Span, LinearAxis
from bokeh.resources import CDN
from scipy.signal import butter, filtfilt

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

output_location_init = '../0_Images/Results/HTML/'

info_file = '../3_Info/Description_of_Experiments.csv'

# Read in channel list
channel_list = pd.read_csv(channel_location+'Channels.csv')

# Set index value for channels as 'Channel'
channel_list = channel_list.set_index('Channel')

# Create groups data by grouping channels for 'Chart'
channel_groups = channel_list.groupby('Chart')

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)

# Set index of description of experiments to Experiment
Exp_Des = Exp_Des.set_index('Experiment')

# Set files to skip in experimental directory
skip_files = ['example']

#Set Tools for Bokeh Plots
TOOLS = 'box_zoom,reset,hover,pan,wheel_zoom'

# Specify name
specific_name = 'Experiment_1_Data'

# Loop through Experiment files
for f in os.listdir(data_location):
	if f.endswith('.csv'):

		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue

		# Read in experiment file
		experiment = f
		Exp_Data = pd.read_csv(data_location + experiment)
		# Exp_Data = Exp_Data.rolling(window=10, center=True).mean()

		# Get experiment name from file
		Test_Name = experiment[:-4]

		print ('--- Loaded ' + Test_Name + ' ---')

		 # uncomment if you want to only plot a single test
		# if specific_name != Test_Name:
		# 	continue

		# Grab experiment number from test name
		Exp_Num = Test_Name[:-5]

		# Set output location for results
		output_location = output_location_init + Test_Name + '/'

		# If the folder exists delete it.
		if os.path.exists(output_location):
			shutil.rmtree(output_location)

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

		# If statements to determine whether or not data is in high speed and assigning time accordingly based on data csv
		if Speed == 'low':
			#Set time to elapsed time column in experimental data.
			Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
			mark_freq = 15

		if Speed == 'high':
			#Set time to elapsed time column in experimental data.
			Time = [datetime.datetime.strptime(t, '%H:%M:%S.%f') for t in Exp_Data['Elapsed Time']]
			mark_freq = 5

		# Pull ignition time from events csv file
		Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

		# Adjust time for ignition offset
		Time = [((t - Ignition).total_seconds())/60 for t in Time]

		# Get End of Experiment Time
		End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60
		
		# Sets scale factor (heat flux constants) and transport time (gas) based on which house the experiment was done in
		if House == 'a':
			scalefactor = 'ScaleFactor_A'
			Transport_Time = 'Transport_Time_A'

		if House == 'b':
			scalefactor = 'ScaleFactor_B'
			Transport_Time = 'Transport_Time_B'

		# Begin plotting

		# Begin cycling through groups 
		for group in channel_groups.groups:

			# Skip excluded groups listed in test description file
			if any([substring in group for substring in Exp_Des['Excluded Groups'][Test_Name].split('|')]):
				continue

			# Define 20 color pallet using RGB values
			tableau20 = cycle([(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
						(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
						(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
						(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
						(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)])
			color=tableau20

			# Print 'Plotting Chart XX'
			print ('Plotting ' + group.replace('_',' '))
			
			# Create figure with set x-axis, set size, and available tools in bokeh package
			output_file(output_location + group + '.html',mode='cdn')
			p = figure( x_axis_label='Time(min)',  height=500, width=1200, tools=TOOLS, title=group.replace('_',' '),x_range = Range1d(0,End_Time))

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
					y_label='Temperature (Degrees F)'
					# Search for skin inside description of events file for scaling
					if 'skin' in group:
						axis_scale = 'Y Scale Skin Temperature'
					else: # Default to standard temperature scale
						axis_scale = 'Y Scale Temperature'
					# Set secondary y-axis label to degrees C
					secondary_axis_label = 'Temperature (Degrees C)'
					#Set scaling dependent on axis scale defined above
					secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) * 5/9 - 32
					hover_value = 'Temperature'
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
					current_data = np.sign(current_data-2.5)*0.070*((Exp_Data[channel[:-1]+'T']+273.15)*(99.6*abs(current_data-2.5)))**0.5
					y_label='Velocity (m/s)'
					line_style = '-'
					axis_scale = 'Y Scale BDP'
					secondary_axis_label = 'Velocity (mph)'
					secondary_axis_scale = np.float(Exp_Des[axis_scale][Test_Name]) * 2.23694
					hover_value = 'Velocity'
                # Set parameters for heat flux plots

				# If statement to find heat flux type in channels csv
				if channel_list['Type'][channel] == 'Heat Flux':
					Data_Time = Time
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					y_label='Heat Flux (kW/m^2)'
					axis_scale = 'Y Scale Heat Flux'
					hover_value = 'Heat Flux'
				# Set parameters for gas plots

				# If statement to find gas type in channels csv
				if channel_list['Type'][channel] == 'Gas':
					Data_Time = [t+float(channel_list[Transport_Time][channel])/60.0 for t in Time]
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					y_label='Gas Concentration (%)'
					axis_scale = 'Y Scale Gas'
					hover_value = 'Gas'

				# If statement to find gas type in channels csv
				if channel_list['Type'][channel] == 'Carbon Monoxide':
					Data_Time = [t+float(channel_list[Transport_Time][channel])/60.0 for t in Time]
					# Set data to include slope and intercept
					current_data = current_data * scale_factor + offset
					plt.ylabel('Gas Concentration (PPM)', fontsize = 16)
					axis_scale = 'Y Scale Carbon Monoxide'

				# Plot channel data with legend from channel list and using tableau colors, in addition to x-axis range
				x= Data_Time
				y= current_data
				channel_label = np.tile(channel_list['Title'][channel],[len(x),1])
				source = ColumnDataSource({'channels':channel_label})
				p.line(x, y, legend=channel_list['Title'][channel], line_width=2, color=next(color),source=source)
				hover=p.select(dict(type=HoverTool))
				hover.tooltips = [('Time','$x{1.11}'),(hover_value,'$y{0.0}'),('Channel','@channels')]
				# Scale y-axis limit based on specified range in test description file
				if axis_scale == 'Y Scale BDP':
					p.y_range = Range1d(-np.float(Exp_Des[axis_scale][Test_Name]),np.float(Exp_Des[axis_scale][Test_Name]))
					p.yaxis.axis_label=y_label
				else:
					p.y_range = Range1d(0,np.float(Exp_Des[axis_scale][Test_Name]))
					p.yaxis.axis_label=y_label

            # Set axis options, legend, tickmarks, etc.

			# Secondary y-axis parameters
			if secondary_axis_label:     
				if axis_scale == 'Y Scale BDP':
					p.extra_y_ranges={secondary_axis_label:Range1d(-secondary_axis_scale,secondary_axis_scale)}
					p.add_layout(LinearAxis(y_range_name=secondary_axis_label, axis_label=secondary_axis_label), 'right')
				elif axis_scale == 'Y Scale Temperature':
					p.extra_y_ranges={secondary_axis_label:Range1d(-17.78,secondary_axis_scale)}
					p.add_layout(LinearAxis(y_range_name=secondary_axis_label, axis_label=secondary_axis_label), 'right')
				else:
					p.extra_y_ranges={secondary_axis_label:Range1d(0,secondary_axis_scale)}
					p.add_layout(LinearAxis(y_range_name=secondary_axis_label, axis_label=secondary_axis_label), 'right')
			try:
				for event in Events.index.values:
						if not event == 'Ignition' and not event =='End Experiment':
							EventTime = (datetime.datetime.strptime(Events['Time'][event], '%H:%M:%S')-Ignition).total_seconds()
							EventLine = Span(location=EventTime/60, dimension='height', line_color='black', line_width=3)
							p.renderers.extend([EventLine])
							p.text(EventTime/60, Exp_Des[axis_scale][Test_Name]*.95, text=[event], angle=1.57, text_align='right')
			except:
				pass
			p.legend.location = "top_left"
			save(p)
			reset_output()