import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt 
import datetime
from bokeh.charts import Scatter, output_file, show
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import HoverTool, Range1d, Span

#Set file locations

data_location = '../2_Data/'

channel_location = '../3_Info/'

chart_location = '../3_Info/'

output_location = '../0_Images/Results/'

# Read in channel list
channel_list = pd.read_csv(channel_location+'Channels.csv')

#Set index value for channels as 'Channel'
channel_list = channel_list.set_index('Channel')

#Create charts data by grouping channels for 'Group'
channels = channel_list.groupby('Chart')

#Read in Charts
chart_list = pd.read_csv(channel_location+'Charts.csv')

#Set index of chart list to the chart name.
charts = chart_list.set_index('Chart')

TOOLS = 'box_zoom,box_select,resize,reset,hover,pan,wheel_zoom'

# Get list of files in 2_Data Directory
experiments = os.listdir(data_location)

#Colors to cycle through for each chart.
Line_Colors = {1:'green', 2:'red',3:'blue',4:'pink',5:'lightgreen',6:'darkblue',7:'goldenrod'}

# Loop through Experiment files
for experiment in experiments:

	if not '.DS_Store' in experiment:

		#Read in experiment file
		Exp_Data = pd.read_csv(data_location + experiment)

		#Get Experiment Name from File
		Test_Name = experiment[:-4]

		#Read in Experiment Events
		Events = pd.read_csv(channel_location + '/Events/' + Test_Name[:-4] + 'Events.csv')

		Events = Events.set_index('Event')

		#Get End of Experiment Time
		End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60

		print (Test_Name)
		
		for chart in charts.index:
			# output to static HTML file
			output_file(output_location + chart + ".html", title=chart.replace('_',' '))

			# create a new plot with a title and axis labels
			p = figure(title=Test_Name.replace('_',' ') + ' ' + chart.replace('_',' '), x_axis_label='Time(min)', y_axis_label=charts['Y_Label'][chart], height=500, width=1200, tools=TOOLS)
			p.x_range = Range1d(0,End_Time)
			p.y_range = Range1d(charts['Y_Min'][chart],charts['Y_Max'][chart])
			
			print ('Plotting ' + chart.replace('_',' '))

			Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
			Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

			Time = [((t - Ignition).total_seconds())/60 for t in Time]
			
			color = 0
			
			for channel in channels.get_group(chart).index.values:
				color = color +1
				scale_factor = channel_list['ScaleFactor'][channel]
				offset = channel_list['Offset'][channel]

				data = Exp_Data[channel] * scale_factor + offset

				p.line(Time, data, legend=channel_list['Title'][channel], line_width=2, color=Line_Colors[color])
			
			for event in Events.index.values:
				if not event == 'Ignition' and not event =='End Experiment':
					EventTime = (datetime.datetime.strptime(Events['Time'][event], '%H:%M:%S')-Ignition).total_seconds()
					EventLine = Span(location=EventTime/60, dimension='height', line_color='black', line_width=3)
					p.renderers.extend([EventLine])
					p.text(EventTime/60, charts['Y_Max'][chart]*.95, text=[event], angle=1.57, text_align='right')#, text_color="firebrick", text_align="left", text_font_size="10pt")

			p.legend.location = "top_left"
			show(p)			
			# save(p)

			
	 
