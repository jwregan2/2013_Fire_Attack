import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt 
import pickle
from itertools import cycle
import os as os
from pylab import * 
import datetime
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
import matplotlib.transforms as mtransforms
from matplotlib.path import Path
import matplotlib.patches as patches
from natsort import natsorted

data_location = '../2_Data/'

tic_location = '../2_Data/TIC_Data/'

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

output_location = '../0_Images/Script_Figures/Experiment_Analysis/Thermal_Imaging_Camera/'

end_time={'Experiment_1':[0,418], 'Experiment_12':[0,326], 'Experiment_17':[0,324], 'Experiment_19':[0,574]}
end_temp_hall={'Experiment_1':700, 'Experiment_12':700, 'Experiment_17':1700, 'Experiment_19':1200}
end_temp_door={'Experiment_1':400, 'Experiment_12':400, 'Experiment_17':600, 'Experiment_19':600}

# If the folder doesn't exist create it.
if not os.path.exists(output_location):
	os.makedirs(output_location)

# establish new variable 
experiments = ['Experiment_1', 'Experiment_12', 'Experiment_17', 'Experiment_19']

for exp in experiments:
	tic_data={}

# Define 17 color pallet using RGB values - Removed Blue due to water flow potting.
	tableau20 = [(255, 127, 14), (255, 187, 120), 
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
	plot_markers = cycle(['s', 'o', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	end_time[exp][1] = end_time[exp][1]/60 

	chart_length = end_time[exp][1] - end_time[exp][0]

	if chart_length > 50:
		mark = int(chart_length * (4/50))
	else: 
		mark = 60 	

# Plot TIC Data for Hall IR
	print (tic_location + exp + '_Data.csv')
	tic_data[exp] = pd.read_csv(tic_location + exp + '_Data.csv')
	tic_data[exp]['Time'] = tic_data[exp]['Time']/60
	tic_data[exp] = tic_data[exp].set_index('Time')

	all_exp_data[exp + '_Data'].index = all_exp_data[exp + '_Data'].index/60

	# print(all_exp_data[exp + '_Data']['1TCV7'].head())
	plt.plot(all_exp_data[exp + '_Data']['1TCV7'], label='7ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(all_exp_data[exp + '_Data']['1TCV5'], label='5ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(all_exp_data[exp + '_Data']['1TCV3'], label='3ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(all_exp_data[exp + '_Data']['1TCV1'], label='1ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(tic_data[exp]['Hall'], label='Hall TIC Temperature', lw=3)
	plt.legend(numpoints=1, loc='upper left')
	plt.grid(linestyle='-',linewidth = 1.5)
	plt.xlim([0,end_time[exp][1]])
	plt.ylim([0,end_temp_hall[exp]])
	plt.xlabel('Time (min)', fontsize=14)
	plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.savefig(output_location + exp + '_Hall.png')
	plt.close()

# Plot TIC Data for Front Door IR
	
	plt.plot(all_exp_data[exp + '_Data']['4TCV7'], label='7ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(all_exp_data[exp + '_Data']['4TCV5'], label='5ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(all_exp_data[exp + '_Data']['4TCV3'], label='3ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(all_exp_data[exp + '_Data']['4TCV1'], label='1ft Temperature', marker=next(plot_markers), markevery=mark, markersize=5)
	plt.plot(tic_data[exp]['Front'], label='Front Door TIC Temperature', lw=3)
	plt.legend(numpoints=1, loc='upper left')
	plt.grid(linestyle='-',linewidth = 1.5)
	plt.xlim([0,end_time[exp][1]])
	plt.ylim([0,end_temp_door[exp]])
	plt.xlabel('Time (min)', fontsize=14)
	plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.savefig(output_location + exp +'_Door.png')
	plt.close()

exit()