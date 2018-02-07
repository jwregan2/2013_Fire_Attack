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

hrr_data_location = '../2_Data/Heat_Release_Data/'
mlr_data_location = '../2_Data/Mass_Loss_Data/'

output_location = '../0_Images/Script_Figures/MLR_HRR/'

HoC_output_location = '../0_Images/Script_Figures/HoC/'

# If the folder doesn't exist create it.
if not os.path.exists(output_location):
	os.makedirs(output_location)

if not os.path.exists(HoC_output_location):
	os.makedirs(HoC_output_location)

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

experiments = ['fireattack_bed_1', 'fireattack_bed_2', 'stripedchair_2', 'stripedchair_3', 'yellowchair_1', 'yellowchair_2','fr_couch1']
print_name = {'fireattack_bed_1':['Bed 1'], 'fireattack_bed_2':['Bed 2'], 'stripedchair_2':['Striped Chair 2'], 'stripedchair_3':['Striped Chair 3'], 'yellowchair_1':['Yellow Chair 1'], 'yellowchair_2':['Yellow Chair 2'], 'fr_couch1':['Couch']}
plots = {'couch':['fr_couch1'], 'all_bed':['fireattack_bed_1', 'fireattack_bed_2'], 'all_striped_chair':['stripedchair_2', 'stripedchair_3'], 'all_yellow_chair':['yellowchair_1', 'yellowchair_2']}

end_time = {'fireattack_bed_1':1532, 'fireattack_bed_2':1532, 'stripedchair_2':1385, 'stripedchair_3':1385, 'yellowchair_1':857, 'yellowchair_2':857, 'fr_couch1':4173}


hrr_data = {}
for exp in experiments:
	hrr_data[exp] = pd.read_csv(hrr_data_location + exp + '.DAT', skiprows=[0,2,3,4])#.set_index('Test Time')
	hrr_data[exp]['Test Time'] = hrr_data[exp]['Test Time']/60
	hrr_data[exp] = hrr_data[exp].set_index('Test Time')
	print(exp + '_hrr')

mlr_data = pd.read_csv(mlr_data_location + 'Mass_Loss_Rate_Data.csv')#.set_index('Seconds')
mlr_data['Seconds'] = mlr_data['Seconds']/60
mlr_data = mlr_data.set_index('Seconds')
print(exp + '_mlr')

for plot in plots.keys():
	fig = plt.figure()
	fig.set_size_inches(8, 6)
	ax1 = fig.add_subplot(111)
	print(plot)
	ax2 = ax1.twinx()
	it = tableau20.__iter__()
	for exp in plots[plot]:
		print('		' + exp)
		ax1.plot(hrr_data[exp]['Heat Release Rate'], label= print_name[exp][0] + ' HRR', color = next(it), lw=1.25, marker=next(plot_markers), markevery=int(mark_freq), mew=1.5,mec='none', ms=6)
		ax2.plot(pd.rolling_mean(-mlr_data[exp].diff(10),10), label= print_name[exp][0] + ' MLR', color = next(it), lw=1.25, marker=next(plot_markers), markevery=int(mark_freq), mew=1.5,mec='none', ms=6)
		ax1.set_xlabel('Time (min)', fontsize=14)
		end_time[exp] = end_time[exp]/60
	plt.xlim([0,end_time[exp]])
	ax1.set_ylabel('Heat Release Rate (kW)',  fontsize=14)
	ax2.set_ylabel('Mass Loss Rate (kg/s)',  fontsize=14)

	h1, l1 = ax1.get_legend_handles_labels()
	h2, l2 = ax2.get_legend_handles_labels()
	ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(0.65, 1), loc='lower left', fontsize=16, handlelength=2, labelspacing=.15)

	ax1.grid(linestyle='-',linewidth = 1.5)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.subplots_adjust(top=0.8, right = 0.85)
	# fig.set_tight_layout(True)
	plt.savefig(output_location + plot + '_HRR_MLR.png')
plt.close('all')

# HoC
fig = plt.figure()
ax = fig.add_subplot(111)

for exp in experiments:

	hrr_data[exp] = pd.read_csv(hrr_data_location + exp + '.DAT', skiprows=[0,2,3,4])
	hrr_data[exp]['Test Time'] = hrr_data[exp]['Test Time']/60
	# hrr_data[exp] = hrr_data[exp].set_index('Test Time')
	print(exp + '_HoC')

	mlr_data = pd.read_csv(mlr_data_location + 'Mass_Loss_Rate_Data.csv')
	mlr_data['Seconds'] = mlr_data['Seconds']/60
	# mlr_data = mlr_data.set_index('Seconds')
	print(exp + '_HoC')

	HoC = (hrr_data[exp]['Heat Release Rate'] / -mlr_data[exp].diff(10))

	df = pd.DataFrame(HoC)
	x = df.replace([-np.inf, np.inf], np.nan).dropna(how='all')
	y = np.mean(x)
	print(y)

	# plot_text = print_name[exp][0] + ' Average HoC: ' + str(y)
	# plt.text(0.55, 0.05, plot_text, horizontalalignment='left', verticalalignment='center',transform = ax.transAxes)

	fig.set_tight_layout(True)
	it = tableau20.__iter__()
	plt.plot(mlr_data['Seconds'], HoC, label= print_name[exp][0] + ' Heat of Combustion', color = next(it), lw=1.25, marker=next(plot_markers), markevery=int(mark_freq), mew=1.5,mec='none', ms=6)
	plt.legend(numpoints=1, loc='upper left')
	plt.xlabel('Time (min)', fontsize=14)
	plt.ylabel('Heat of Combustion (kJ/kg)', fontsize=14)
	plt.grid(linestyle='-',linewidth = 1.5)
	plt.xticks(fontsize=16)
	plt.yticks(fontsize=16)
	plt.savefig(HoC_output_location + exp + '_HoC.png')
	plt.close('all')

exit()