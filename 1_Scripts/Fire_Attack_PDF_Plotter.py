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

info_file = '../3_Info/Description_of_Experiments.csv'

# Read in channel list
channel_list_a = pd.read_csv(channel_location+'Channels_A.csv')

channel_list_b = pd.read_csv(channel_location+'Channels_B.csv')

#Set index value for channels as 'Channel'
channel_list_a = channel_list_a.set_index('Channel')

channel_list_b = channel_list_b.set_index('Channel')

#Create charts data by grouping channels for 'Chart'
channels_a = channel_list_a.groupby('Chart')

channels_b = channel_list_b.groupby('Chart')

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

Exp_Des = pd.read_csv(info_file)

Exp_Des = Exp_Des.set_index('Experiment')

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

		Exp_Num = Test_Name[:-5]

		House = Exp_Des['House'][int(Exp_Num[11:])]

		Speed = Exp_Des['Speed'][int(Exp_Num[11:])]

		#Read in Experiment Events
		Events = pd.read_csv(channel_location + '/Events/' + Test_Name[:-4] + 'Events.csv')

		Events = Events.set_index('Event')

		#Get End of Experiment Time
		End_Time = (datetime.datetime.strptime(Events['Time']['End Experiment'], '%H:%M:%S')-datetime.datetime.strptime(Events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60

		print (Test_Name)
		
		if House == 'a':
			channels = channels_a
			channel_list = channel_list_a

		if House == 'b':
			channels = channels_b
			channel_list = channel_list_b
