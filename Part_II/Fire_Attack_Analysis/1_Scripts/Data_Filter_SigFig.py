#Averages the data from the high speed samples from 100hz to 10hz to 
# allow them to be placed on gitHub. Data is resampled using a moving 
# average of each of 10 points. 

import os as os
import pandas as pd 
import matplotlib.pyplot as plt
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

#Set High Speed Data Location
data_location = '../2_Data/'

# Get list of files in 2_Data Directory
experiments = os.listdir(data_location)

for experiment in experiments:
	
	if '.csv' in experiment:
		Exp_Data = pd.read_csv(data_location + experiment)

		for channel in Exp_Data:
			if 'Time' in channel:
				continue
			elif 'TC' in channel:
				Exp_Data[channel] = Exp_Data[channel].map(lambda x: '%2.1f' % x)
			elif 'HF' in channel:
				Exp_Data[channel] = Exp_Data[channel].map(lambda x: '%1.5f' % x)
			elif 'BDP' and 'V' in channel:
				Exp_Data[channel] = Exp_Data[channel].map(lambda x: '%1.4f' % x)
			elif 'PT' in channel:
				Exp_Data[channel] = Exp_Data[channel].map(lambda x: '%1.3f' % x)
			elif 'BDP' and 'T' in channel:
				Exp_Data[channel] = Exp_Data[channel].map(lambda x: '%2.1f' % x)
			elif 'HUMS' in channel:
				Exp_Data[channel] = Exp_Data[channel].map(lambda x: '%1.3f' % x)
			else:
				Exp_Data[channel] = Exp_Data[channel].map(lambda x: '%2.3f' % x)

		Exp_Data.to_csv(data_location + '/Smaller_Data/' + experiment, index=False)





