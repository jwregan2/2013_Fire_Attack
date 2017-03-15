import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import datetime
import os 

data_location = '../0_Data/Fire_Experiment_Data'
info_location = '../1_Info'
output_location = '../2_Plots/Fire_Experiment_Plots'

channels = pd.read_csv(info_location + '/Channels_List.csv')
channels = channels.set_index('Channel')
channel_groups = channels.groupby('Chart')


experiments = [1,2,3,4,5,6]


for exp in experiments:

	data = pd.read_csv(data_location + '/Fire_Experiment_' + str(exp) + '.csv')

	events = pd.read_csv(data_location + '/Fire_Experiment_' + str(exp) + '_Events.csv')
	events = events.set_index('Event')
	# If the folder doesn't exist create it.
	
	if not os.path.exists(output_location + '/Fire_Experiment_' + str(exp)):
		os.makedirs(output_location + '/Fire_Experiment_' + str(exp))

	ignition = datetime.datetime(year=1, month=1, day=1, hour=0, minute=0, second=1)

	time_start = datetime.datetime.strptime(events['Time']['Ignition'], '%Y-%m-%d-%H:%M:%S')

	time = [(datetime.datetime.strptime(t, '%H:%M:%S')-time_start).total_seconds() for t in data['Elapsed Time']]

	for channel_group in channel_groups.groups:

		for channel in channel_groups.get_group(channel_group).index.values:

			plot_data = data[channel]*channels['Slope'][channel]+channels['Offset'][channel]

			if 'BDP' in channel:
				plot_data = plot_data - data[channel][15:105].mean()
				plot_data = np.sign(plot_data)*0.07*np.sqrt(data[channel[:-1]+'T']*1.8+305*abs(plot_data))
				plt.axhline(y=0, color='black', lw=2)
			if 'PT' in channel:
				plot_data = plot_data - data[channel][15:105].mean()
				plt.axhline(y=0, color='black', lw=2)

			plt.plot(time,plot_data, label=channel)

		if 'BDP' in channel_group:
			plt.ylabel('Velocity(m/s)', fontsize=32)
		if 'TC' in channel_group:
			plt.ylabel('Temperature ($^\circ$F)', fontsize=32)
		if 'PT' in channel_group:
			plt.ylabel('Pressure (Pa)', fontsize=32)
		
		plt.xlabel('Time (min)', fontsize=32)
		plt.xticks(fontsize=28)
		plt.yticks(fontsize=28)
		plt.savefig(output_location + '/Fire_Experiment_' + str(exp) + '/' + channel_group + '.pdf')


		plt.close('all')

exit()
