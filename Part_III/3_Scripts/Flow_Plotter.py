import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import datetime

channels = pd.read_csv('Prop_A_Channels.csv')
channels = channels.set_index('Channel')
channel_groups = channels.groupby('Group')


data = pd.read_csv('Experiment_1.csv')

for channel_group in channel_groups.groups:

	for channel in channel_groups.get_group(channel_group).index.values:

		zero = data[channel][15:45].mean()

		ignition = datetime.datetime(year=1, month=1, day=1, hour=0, minute=0, second=1)

		time_start = datetime.datetime.strptime(data['Elapsed Time'][0], '%H:%M:%S')

		time = [(datetime.datetime.strptime(t, '%H:%M:%S')-time_start).total_seconds() for t in data['Elapsed Time']]

		plot_data = (data[channel] - zero) + 2.5

		if 'BDP' in channel:
			plot_data = np.sign(plot_data-2.5)*0.07*np.sqrt(280*abs(9.964*plot_data-24.91))*185.5*2.5

			plt.plot(time,plot_data, label=channel)
		else:
			plot_data = np.sign(plot_data-2.5)*(plot_data*49.81-124.54)


			plt.plot(time,plot_data, label=channel)
	
		plt.axhline(y=0, color='black', lw=2)
		plt.savefig(channel_group + '.pdf')


	plt.close('all')

exit()
