import pandas as pd
import datetime as dt 
import os
import numpy as np

info_location = '../3_Info/'
data_location = '../2_Data/'

files = os.listdir(info_location + 'Events/')

all_events = pd.DataFrame()
fd_open_min = 0

Vent_Info=pd.read_csv(info_location+'Vent_Info.csv', dtype='object')

for Vent_Type in Vent_Info.columns:

	Vent_Type_Exp = Vent_Info[Vent_Type].values

	for exp in Vent_Type_Exp:

		if exp is np.nan:
			continue

		events = pd.read_csv(info_location + 'Events/Experiment_' + str(exp) + '_Events.csv')
		events = events.set_index(events['Event'])

		fd_open = (dt.datetime.strptime(events['Time']['Front Door Open'], '%H:%M:%S') - dt.datetime.strptime(events['Time']['Ignition'], '%H:%M:%S')).total_seconds()/60	
		
		if fd_open_min is 0:
			fd_open_min = fd_open
		elif fd_open_min > fd_open:
			fd_open_min = fd_open

	print (Vent_Type + ' earliest front door open is ' + str(fd_open_min))

