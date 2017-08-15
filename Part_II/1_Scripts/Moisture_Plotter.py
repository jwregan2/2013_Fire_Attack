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

data_location = '../2_Data/'
info_location = '../3_Info/'
output_location = '../0_Images/Script_Figures/Experiment_Analysis/'

if not os.path.exists(output_location):
	os.makedirs(output_location)

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

all_flow_data = pickle.load(open(data_location + 'all_flow_data.dict', 'rb'))

all_exp_events = pickle.load(open(info_location + '/Events/all_exp_events.dict', 'rb'))

all_channels = pd.read_csv(info_location + 'Channels.csv').set_index('Channel')
all_gas_channels = pd.read_csv(info_location + 'Gas_Channels.csv').set_index('Channel')

Exp_Des = pd.read_csv(info_location + 'Description_of_Experiments.csv').set_index('Experiment')

channels_to_skip = {}

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

plt.plot(all_exp_data['Experiment_18_Data'].index/60, all_exp_data['Experiment_18_Data']['3TC7'])
plt.plot(all_flow_data['Experiment_18_Data'].index/60, all_flow_data['Experiment_18_Data']['GPM'])
plt.xlim([0,10])
plt.show()

# print ('-------------------------------------- Developing Moisture Table ----------------------------------')

# data_location_moisture = data_location + 'Laser/'

# experiments = os.listdir(data_location_moisture)

# exp_info = pd.read_csv(info_location + 'Moisture_Info.csv').set_index('Experiment')
# exp_info_grouped = exp_info.groupby('Vent')

# all_laser_data = {}
# low = pd.DataFrame()
# high = pd.DataFrame()

# for exp in sorted(experiments):
# 	if exp.endswith('.csv'):
# 		all_laser_data[exp[:-4]] = pd.read_csv(data_location_moisture + exp).set_index('Time')

# 		flow_time = all_exp_events[exp[:-4]+'_Events']['Flow_Time'].min()

# 		# print (flow_time/60)
# 		time = flow_time+45


# 		inter = all_laser_data[exp[:-4]][all_laser_data[exp[:-4]].index > time/60].iloc[0].max()

# 		if inter == 0:
# 			low = all_laser_data[exp[:-4]][all_laser_data[exp[:-4]].index < time/60]['Low'].max()
# 			high = all_laser_data[exp[:-4]][all_laser_data[exp[:-4]].index < time/60]['High'].max()
# 			inter = max([low,high])

# 		plt.plot(all_laser_data[exp[:-4]]['High'], label=exp)
# 		# plt.plot(all_laser_data[exp[:-4]]['High'])
# 		# print(exp[:-4])
# 		# print (inter)
# 		# print (time)




# 		# if all_laser_data[exp[:-4]][all_laser_data[exp[:-4]].index > all_exp_events[exp[:-4]+'_Events']['Time_Seconds'][1]/60].iloc[0].max() == 0:
# 		# 	low = all_laser_data[exp[:-4]][all_laser_data[exp[:-4]].index < all_exp_events[exp[:-4]+'_Events']['Time_Seconds'][1]/60]['Low'].max()
# 		# 	high = all_laser_data[exp[:-4]][all_laser_data[exp[:-4]].index < all_exp_events[exp[:-4]+'_Events']['Time_Seconds'][1]/60]['High'].max()
# 		# 	print (exp[:-4] + ' ' + str(max([low,high])))
# 		# else:
# 		# 	print (exp[:-4] + ' ' + str(all_laser_data[exp[:-4]][all_laser_data[exp[:-4]].index > all_exp_events[exp[:-4]+'_Events']['Time_Seconds'][1]/60].iloc[0].max()))
# # plt.plot(all_laser_data['Experiment_16']['Low'], color='pink')
# # plt.plot(all_laser_data['Experiment_16']['High'], color='pink')
# # plt.plot(all_laser_data['Experiment_10']['Low'], color='purple')
# # plt.plot(all_laser_data['Experiment_10']['High'], color='purple')
# # plt.plot(all_laser_data['Experiment_19']['Low'], color='orange')
# # plt.plot(all_laser_data['Experiment_19']['High'], color='orange')
# # plt.plot(all_laser_data['Experiment_18']['Low'], color='green')
# # plt.plot(all_laser_data['Experiment_18']['High'], color='green')
# # plt.plot(all_laser_data['Experiment_4']['Low'], color='blue')
# # plt.plot(all_laser_data['Experiment_4']['High'], color='blue')
# # plt.plot(all_laser_data['Experiment_21']['Low'], color='red')
# # plt.plot(all_laser_data['Experiment_21']['High'], color='red')
# plt.xlim([0,10])
# plt.ylim([0,9])
# plt.legend()
# # plt.axvline(6+52/60, color='black')
# # plt.axvline(7+46/60, color='black')
# plt.show()

# exit()


