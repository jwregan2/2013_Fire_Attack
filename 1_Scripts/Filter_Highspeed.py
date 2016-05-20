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
data_location = '../../../../Desktop/FireAttackData/'

# Get list of files in 2_Data Directory
experiments = os.listdir(data_location)

for experiment in experiments:
	
	if '.csv' in experiment:

		Exp_Data = pd.read_csv(data_location + experiment)

		Exp_Data['Elapsed Time'] = pd.to_datetime(Exp_Data['Elapsed Time'], unit='s')

		Exp_Data = Exp_Data.set_index(Exp_Data['Elapsed Time'])
		
		New_Data = Exp_Data.resample('100L').mean()

		New_Data.to_csv(data_location + '/Resampled_Data/' + experiment)

