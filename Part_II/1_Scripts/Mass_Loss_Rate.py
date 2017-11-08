import pandas as pd 
import os as os
import numpy as np 
from pylab import * 
from datetime import datetime, timedelta
import shutil
from dateutil.relativedelta import relativedelta
from scipy.signal import butter, filtfilt
from itertools import cycle
from scipy.signal import butter, filtfilt, resample

data_location = '../2_Data/HRR_Mass_Loss/'

output_location = '../0_Images/Script_Figures/MLR/'

# If the folder doesn't exist create it.
if not os.path.exists(output_location):
	os.makedirs(output_location)

experiments = ['FireAttack_Bed1', 'FireAttack_Bed2', 'Couch1_CenterIgnite', 'Couch3_RightIgnite', 'Couch2_LeftIgnite', 'StripedChair_1', 'StripedChair_2', 'StripedChair_3', 'YellowChair_1', 'YellowChair_2']
print_name = {'FireAttack_Bed1':['Bed 1'], 'FireAttack_Bed2':['Bed 2'], 'Couch1_CenterIgnite':['Sofa Center Ignition'], 'Couch2_LeftIgnite':['Sofa Left Ignition'], 'Couch3_RightIgnite':['Sofa Right Ignition'], 'StripedChair_1':['Striped Chair 1'], 'StripedChair_2':['Striped Chair 2'], 'StripedChair_3':['Striped Chair 3'], 'YellowChair_1':['Yellow Chair 1'], 'YellowChair_2':['Yellow Chair 2']}

for exp in experiments:

#Define color pallet
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

	mark_freq = 60

# Graph MLR for Each Experiment

	data = pd.read_csv(data_location + 'Mass_Loss_Rate_Data.csv').set_index('Seconds')
	fig = plt.figure()
	ax = fig.add_subplot(111)
	fig.set_tight_layout(True)
	plt.plot(data[exp], marker=next(plot_markers), markevery=int(mark_freq), markersize=5)
	plot_text = print_name[exp]
	plt.legend(plot_text, numpoints=1, loc='upper right')
	plt.grid(linestyle='-',linewidth = 1.5)
	plt.ylabel('Mass Loss (kg)', fontsize=16)
	plt.xlabel('Time (s)', fontsize=16)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.savefig(output_location + exp + '.png')
	plt.close('all')
