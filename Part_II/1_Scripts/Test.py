import pandas as pd
import os
import datetime as datetime
import numpy as np
from scipy.signal import butter, filtfilt,savgol_filter
import pickle
import math
import matplotlib.pyplot as plt


data = pd.read_csv('../2_Data/Experiment_18_Data.csv')

data['Time'] = pd.to_datetime(data['Time'])

data.set_index('Time', inplace=True)

flow = datetime.datetime(year=2016, month=3, day=2, hour=9, minute=34, second=59)

start = flow - datetime.timedelta(seconds=30)
end = flow + datetime.timedelta(seconds=30)

flow_time = flow - data.index[0]

print (flow_time)
# exit()

plt.plot(data['1BDP1V'], label='1')
plt.plot(data['1BDP2V'], label='2')
plt.plot(data['1BDP3V'], label='3')
plt.plot(data['1BDP4V'], label='4')
plt.plot(data['1BDP5V'], label='5')

plt.legend()
plt.axvline(flow)
plt.axhline(2.5, color='black')

plt.xlim([start,end])
plt.ylim([2,3])

plt.show()



