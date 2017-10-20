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

data_location = '../2_Data/Free_Burn_Data/'

output_location = '../0_Images/Script_Figures/HRR/'

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

# Plot all like furniture together 

experiments = ['fireattack_bed_1', 'fireattack_bed_2', 'sofa_center_ignite', 'sofa_right_ignite', 'sofa_left_ignite', 'stripedchair_1', 'stripedchair_2', 'stripedchair_3', 'yellowchair_1', 'yellowchair_2']

all_HRR_data = {}
for exp in experiments:
	all_HRR_data[exp] = pd.read_csv(data_location + exp + '.DAT', skiprows=[0,2,3,4]).set_index('Test Time')
	print(exp)

plots = {'all_sofa':['sofa_center_ignite', 'sofa_right_ignite', 'sofa_left_ignite'], 'all_bed':['fireattack_bed_1', 'fireattack_bed_2'], 'all_striped_chair':['stripedchair_1', 'stripedchair_2', 'stripedchair_3'], 'all_yellow_chair':['yellowchair_1', 'yellowchair_2']}
for plot in plots.keys():
	print(plot)

	for exp in plots[plot]:
		print('		' + exp)
		plt.plot(all_HRR_data[exp]['Heat Release Rate'], lw=1.25, marker=next(plot_markers), markevery=int(mark_freq), mew=1.5,mec='none', ms=6, label= exp + '_HRR')

	plt.legend(numpoints=1, loc='upper right')
	plt.grid(linestyle='-',linewidth = 1.5)
	plt.ylabel('Heat Release Rate (kW)')
	plt.xlabel('Time (s)', fontsize=16)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.tight_layout()
	plt.savefig(output_location + plot + '.png')
	plt.close()
exit()