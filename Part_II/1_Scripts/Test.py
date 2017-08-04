import pandas as pd
import os
import datetime as datetime
import numpy as np
from scipy.signal import butter, filtfilt,savgol_filter
import pickle
import math
import matplotlib.pyplot as plt


flow_data = pd.read_csv('../2_Data/Experiment_25_Flow.csv')

flow_data['Time'] = flow_data['Time'].str[3:]

flow_data.to_csv('../2_Data/Experiment_25_Flow_new.csv', index=False)

