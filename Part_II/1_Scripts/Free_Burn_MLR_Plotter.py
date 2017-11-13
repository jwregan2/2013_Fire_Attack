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

data_location = '../2_Data/Mass_Loss_Data/'

output_location = '../0_Images/Script_Figures/MLR/'

# If the folder doesn't exist create it.
if not os.path.exists(output_location):
	os.makedirs(output_location)

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

# To Label Plots with Peak HRR
fig = plt.figure()
ax = fig.add_subplot(111)

# Plot all like furniture together 

experiments = ['fireattack_bed_1', 'fireattack_bed_2', 'stripedchair_2', 'stripedchair_3', 'yellowchair_1', 'yellowchair_2', 'fr_couch1']
print_name = {'fireattack_bed_1':['Bed 1'], 'fireattack_bed_2':['Bed 2'], 'stripedchair_2':['Chair 2'], 'stripedchair_3':['Chair 3'], 'yellowchair_1':['Chair 1'], 'yellowchair_2':['Chair 2'], 'fr_couch1':['Couch']}
end_time = {'fireattack_bed_1':1532, 'fireattack_bed_2':1532, 'stripedchair_2':1385, 'stripedchair_3':1385, 'yellowchair_1':857, 'yellowchair_2':857, 'fr_couch1':4173}

all_MLR_data = pd.read_csv(data_location + 'Mass_Loss_Rate_Data.csv').set_index('Seconds')
print(exp)

plots = {'couch':['fr_couch1'], 'all_bed':['fireattack_bed_1', 'fireattack_bed_2'], 'all_striped_chair':['stripedchair_2', 'stripedchair_3'], 'all_yellow_chair':['yellowchair_1', 'yellowchair_2']}
for plot in plots.keys():
	print(plot)

	height = 0 
	for exp in plots[plot]:
		print('		' + exp)
		plt.plot(all_MLR_data[exp], lw=1.25, marker=next(plot_markers), markevery=int(mark_freq), mew=1.5,mec='none', ms=6, label= print_name[exp][0] + ' MLR')
	plt.xlim([0,end_time[exp]])
	plt.legend(numpoints=1, loc='upper right')
	plt.grid(linestyle='-',linewidth = 1.5)
	plt.ylabel('Mass Loss (kg)', fontsize=16)
	plt.xlabel('Time (s)', fontsize=16)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	fig.tight_layout()
	plt.savefig(output_location + plot + '_MLR.png')
	plt.close('all')

exit()
