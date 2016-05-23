import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt 
import datetime
import shutil
from bokeh.charts import Scatter, output_file, show
from dateutil.relativedelta import relativedelta
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import HoverTool, Range1d, Span
from scipy.signal import butter, filtfilt


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

#Set Chart Type

chart_type = '.pdf'

#Set file locations
data_location = '../2_Data/'

channel_location = '../3_Info/'

chart_location = '../3_Info/'

output_location = '../0_Images/Results/'

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

#Set Tools for Bokeh Plots
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

		output_location = output_location + Test_Name + '/'

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

		if chart_type == '.pdf':

			for chart in charts.index:
				# output to static HTML file
				output_file(output_location + chart +chart_type, title=chart.replace('_',' '))

				# create a new plot with a title and axis labels
				p = figure(title=Test_Name.replace('_',' ') + ' ' + chart.replace('_',' '), x_axis_label='Time(min)', y_axis_label=charts['Y_Label'][chart], height=500, width=1200, tools=TOOLS)
				p.x_range = Range1d(0,End_Time)
				p.y_range = Range1d(charts['Y_Min'][chart],charts['Y_Max'][chart])
				
				Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
				Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

				Time = [((t - Ignition).total_seconds())/60 for t in Time]
				
				color = 0
				
				if charts['Type'][chart] == 'Standard':

					print ('Plotting ' + chart.replace('_',' '))

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
							p.text(EventTime/60, charts['Y_Max'][chart]*.95, text=[event], angle=1.57, text_align='right')

					p.legend.location = "top_left"
					save(p)			

				if charts['Type'][chart] == 'Calculated':

					print ('Plotting ' + chart.replace('_',' '))

					for channel in calculated_channels.get_group(chart).index.values:
						color = color +1
						
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

						#Caculate result
						data = np.sign(press_data-2.5)*0.070*((temp_data+273.15)*(99.6*abs(press_data-2.5)))**0.5

						p.line(Time, data, legend=channel, line_width=2, color=Line_Colors[color])

						ZeroLine = Span(location=0, dimension='width', line_color='black')
						p.renderers.extend([ZeroLine])

					for event in Events.index.values:
						if not event == 'Ignition' and not event =='End Experiment':
							EventTime = (datetime.datetime.strptime(Events['Time'][event], '%H:%M:%S')-Ignition).total_seconds()
							EventLine = Span(location=EventTime/60, dimension='height', line_color='black', line_width=3)
							p.renderers.extend([EventLine])
							p.text(EventTime/60, charts['Y_Max'][chart]*.95, text=[event], angle=1.57, text_align='right')

					p.legend.location = "top_left"
					save(p)
					#show(p)
		else:
				for chart in charts.index:
					# output to static HTML file
					output_file=output_location + chart +chart_type
					#output_title=chart.replace('_',' ')

					# create a new plot with a title and axis labels
					fig=plt.figure()
					ax=plt.gca()
					
					title=Test_Name.replace('_',' ') + ' ' + chart.replace('_',' ')
					plt.xlim(0,End_Time)
					plt.ylim(charts['Y_Min'][chart],charts['Y_Max'][chart])
					plt.xlabel('Time(min)', fontsize=20)
					plt.ylabel(charts['Y_Label'][chart],fontsize=20)
				
					Time = [datetime.datetime.strptime(t, '%H:%M:%S') for t in Exp_Data['Elapsed Time']]
					Ignition = datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')

					Time = [((t - Ignition).total_seconds())/60 for t in Time]
				
					color = 0
				
					if charts['Type'][chart] == 'Standard':

						print ('Plotting ' + chart.replace('_',' '))

						for channel in channels.get_group(chart).index.values:
							color = color +1
							scale_factor = channel_list['ScaleFactor'][channel]
							offset = channel_list['Offset'][channel]
						
							data = Exp_Data[channel] * scale_factor + offset
							
							plt.plot(Time, data,  lw=2, color=Line_Colors[color])

						
						ax2=plt.twiny()
						ax2.set_xlim(0,End_Time)
						EventTime=range(len(Events.index.values))

						for i in range(len(Events.index.values)):
							#if not Events.index.values[i] == 'Ignition' and not Events.index.values[i] =='End Experiment':
				

								EventTime[i] = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%H:%M:%S')-Ignition).total_seconds()
								#EventLine = Span(location=EventTime/60, dimension='height', line_color='black', line_width=3)

								plt.axvline(EventTime[i],color='.01',lw=1) 

						ax2.set_xticks(EventTime)
						plt.setp(plt.xticks()[1], rotation=30)		
						ax2.set_xticklabels(Events.index.values, fontsize=8, ha='left')
						handles1,labels1=ax.get_legend_handles_labels()


						plt.legend(handles1,labels1, loc='upper left',fontsize=8,handlelength=3)
						plt.savefig(output_file)#+'/'+chart)
						plt.close('all')

					if charts['Type'][chart] == 'Calculated':
						print ('Plotting ' + chart.replace('_',' '))

						for channel in calculated_channels.get_group(chart).index.values:
							color = color +1
							
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

							#Caculate result
							data = np.sign(press_data-2.5)*0.070*((temp_data+273.15)*(99.6*abs(press_data-2.5)))**0.5

											
							plt.plot(Time, data,  lw=2, color=Line_Colors[color])
							
							ax2=plt.twiny()
							ax2.set_xlim(0,End_Time)
							
							plt.axvline(0,color='.01',lw=1)
							EventTime=range(len(Events.index.values))

						for i in range(len(Events.index.values)):
							#if not Events.index.values[i] == 'Ignition' and not Events.index.values[i] =='End Experiment':
									EventTime[i] = (datetime.datetime.strptime(Events['Time'][Events.index.values[i]], '%H:%M:%S')-Ignition).total_seconds()
									#EventLine = Span(location=EventTime/60, dimension='height', line_color='black', line_width=3)
									plt.axvline(EventTime[i],color='.01',lw=1) 
									#p.text(EventTime/60, charts['Y_Max'][chart]*.95, text=[event], angle=1.57, text_align='right')
						ax2.set_xticks(EventTime)
						plt.setp(plt.xticks()[1], rotation=30)
						ax2.set_xticklabels(Events.index.values, fontsize=8, ha='left')
						andles1,labels1=ax.get_legend_handles_labels()
						labels1= calculated_channels.get_group(chart).index.values
						plt.legend(handles1,labels1, loc='upper left',fontsize=8,handlelength=3)
						plt.savefig(output_file)
						plt.close('all')
						#show(p)

			 
