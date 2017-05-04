import os

data_location = '//uscmbl101p/CMB_SharedFiles/02 - FSRI Active Projects/DHS 2013 - Fire Attack/02 - Experiments/04 - Building 11 Fire Experiments/Experiment_1/'
data_location = "//uscmbl101p/CMB_SharedFiles"
# Experimental_Data/TDMS/Experiment_1.tdms'

files = os.listdir('~/Desktop/FireAttack_TDMS/')

print (files)

if os.path.isfile(data_location + 'Experimental_Data/TDMS/Experiment_1.tdms'):
	print ('Experimental_Data/TDMS/Experiment_1.tdms exists')