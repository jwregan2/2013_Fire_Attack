import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pylab import * 
from itertools import cycle

data_dir = '../CSV_Data/'
info_file = '../Info/Description_of_Experiments.csv'
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Original_Test_Name')
skip_files = ['water','15-04-13']
bin_file = '../Info/bin_map.csv'
bin_data = pd.read_csv(bin_file)

for f in os.listdir(data_dir):
	if f.endswith('.csv'):

		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue
		
		# Read in experiment file
		experiment = f

		Test_Name = experiment[:-4]
		if Exp_Des['Test_Config'][Test_Name] == 'ignore':
			continue
		data = pd.read_csv(data_dir + experiment)

		init_water = 0
		final_water = 0
		for i in range(1,49):
			init_water = data['Pressure_'+str(i)+'- Scaled'].iloc[0] + init_water
			final_water = data['Pressure_'+str(i)+'- Scaled'].iloc[-1] + final_water

		for k in range(len(data)):
			water_flow = 0
			for i in range(1,49):
				water_flow = data['Pressure_'+str(i)+'- Scaled'].iloc[k]+water_flow
			if (water_flow - init_water) > 10:
				break
		for kk in range(len(data)):
			water_flow = 0
			for i in range(1,49):
				water_flow = data['Pressure_'+str(i)+'- Scaled'].iloc[kk]+water_flow
			if (final_water-water_flow) < 10:
				break
		if Test_Name == '15-12-08_104620_Datafile':
			kk = 90

		rate_water_buckets = []
		for i in range(1,49):
			temp = data['Pressure_'+str(i)+'- Rate'].iloc[k:kk].mean()
			rate_water_buckets.append(temp)

		dx = 0.5
		dy = 0.5

		X = []
		Y = []
		for x in range (1,9):
			for y in range(1,7):
				X.append(x)
				Y.append(y)

		rate_water = []
		for row in range(len(bin_data)):
			rate_water.append(abs(rate_water_buckets[bin_data['bin'][row]-1])/bin_data['area'][row])

		cs = ["" for x in range(len(rate_water))]
		for i in range(len(rate_water)):
			if rate_water[i] <= 3:
				cs[i] = 'b'
			elif rate_water[i] > 3 and rate_water[i] <= 6:
				cs[i] = 'g'
			elif rate_water[i] > 6 and rate_water[i] <= 9:
				cs[i] = 'gold'
			elif rate_water[i] > 9:
				cs[i] = 'r'

		if Exp_Des['Nozzle_Type'][f[:-4]] == 'Smooth Bore':
			Test_Name2 = str(Exp_Des['Tip_Size_(in)'][f[:-4]]) + '"' + ' ' + str(Exp_Des['Nozzle_Type'][f[:-4]]) + ' ' + str(Exp_Des['Location'][f[:-4]])
		elif Exp_Des['Nozzle_Type'][f[:-4]] == 'Fog' or 'Straight Stream':
			Test_Name2 = str(Exp_Des['Nozzle_Type'][f[:-4]]) + ' ' + str(Exp_Des['Location'][f[:-4]])

		Vents = Exp_Des['Vent_Configuration'][f[:-4]]
		Nozzle_Setting = str(int(Exp_Des['Flow_Rate_(gpm)'][f[:-4]]))+'gpm'+ ' ' + '@' + ' '+str(int(Exp_Des['Nozzle_Pressure_(psi)'][f[:-4]]))+'psi'
		Nozzle_Position = str(Exp_Des['Nozzle_Position'][f[:-4]])+ ','+' '+str(Exp_Des['Nozzle_Direction'][f[:-4]])
		Nozzle_Pattern = str(Exp_Des['Nozzle_Pattern'][f[:-4]])+' '+'Pattern'
		Hoseline_Size = str(Exp_Des['Hose_Line_Size'][f[:-4]])+'"'+' '+'Hose'
		Location = str(Exp_Des['Location'][f[:-4]])

		print (Test_Name + ' ' + Test_Name2)

		row_num = 6
		col_num = 8
		ticksx = np.arange(0, col_num, 1)
		ticksy = np.arange(0, row_num, 1)
		column_names = ['1','2','3','4','5','6','7','8']
		row_names = ['1','2','3','4','5','6']

		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		ax.bar3d(X, Y, np.zeros(len(rate_water)), dx, dy, rate_water, zsort='max',color=cs)
		ax.view_init(elev=48., azim=-160)
		ax.text(15, 4.5, 8.5,Test_Name2, horizontalalignment='left', verticalalignment='bottom')
		ax.text(15, 4.5, 7,Hoseline_Size + ',' + ' ' + Nozzle_Setting, horizontalalignment='left', verticalalignment='bottom')
		ax.text(15, 4.5, 5.5,Nozzle_Position, horizontalalignment='left', verticalalignment='bottom')
		ax.text(15, 4.5, 4,Nozzle_Pattern, horizontalalignment='left', verticalalignment='bottom')

		ax.set_zlim(0,12)
		ax.set_xlabel('Window Side (# of Bins)')
		ax.set_ylabel('Door Side (# of Bins)')
		ax.set_zlabel('Water Flux (gpm/ft$^2$)')
		plt.savefig('../../Report/Script_Figures/ADD_Analysis/' + f[:-4] + '_Rate_' + Test_Name2.replace('/','_').replace('"','in').replace(' ','_') + '.pdf')

		plt.close('all')
