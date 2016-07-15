import numpy as np 
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D
from scipy.special import jn
import ntpath
# from Tkinter import Tk
# from tkFileDialog import askopenfilename
import os
import operator
import pandas as pd


# Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
# filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file

import csv

data_dir = 'CSV_Data/'

info_file = 'Description_of_Experiments.csv'

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)

# Set index of description of experiments to Experiment
Exp_Des = Exp_Des.set_index('Original_Test_Name')

for f in os.listdir(data_dir):
	if f.endswith('.csv'):
		
		with open ((data_dir+f), 'r') as csvfile:
		# with open ('Test.csv') as csvfile:
			csvfile.readline()
			GraphData =  csv.reader(csvfile, delimiter=',')

			ExpData = []
			
			for line in GraphData:
				ExpData.append(line)

		if Exp_Des['Test_Config'][f[:-4]] == 'ignore':
			continue

		dx = 0.5
		dy = 0.5

		BinData = []

		for c in range(74,74+49):
			BinDat = list(x[c] for x in ExpData)
			BinData.append(list(map(float,BinDat)))

		# print BinData

		X = []
		Y = []

		for x in range (1,9):
			for y in range(1,7):
				X.append(x)
				Y.append(y)

		Zmap = [41,42,1,2,5,6,43,44,3,4,7,8,45,46,9,10,13,14,47,48,11,12,15,16,33,34,17,18,21,22,35,36,19,20,23,24,37,38,25,26,29,30,39,40,27,28,31,32]

		Zstart = []
		Zend =[]

		Z1 = []
		Z2 = []
		Z3 = []
		Z4 = []
		Z5 = []

		for row in range(0,48):
			Z1.append(BinData[Zmap[row]-1][0])
			Z2.append(BinData[Zmap[row]-1][1])
			Z3.append(BinData[Zmap[row]-1][2])
			Z4.append(BinData[Zmap[row]-1][3])
			Z5.append(BinData[Zmap[row]-1][4])
			Zend.append(BinData[Zmap[row]-1][len(BinData[0])-1])

		Zgraph = []

		for v in range (0, len(Z1)):
			Zstart.append((Z1[v]+ Z2[v]+Z3[v]+Z4[v]+Z5[v])/5)

		for value in range(0,len(Zstart)):
			if Zend[value]-Zstart[value] > 10:
				Zgraph.append(10)
			else:
				Zgraph.append(Zend[value]-Zstart[value])

		# print X[0:8]
		# print Y[0:8]
		# print Zgraph[0:8]

		# fig = plt.figure()
		# ax = fig.add_subplot(111, projection='3d')
		# # ax = Axes3D(plt.figure())
		# ax.bar3d(X, Y, np.zeros(len(Zgraph)), dx, dy, Zgraph, zsort='max')
		# ax.view_init(elev=48., azim=-160)
		# ax.text(10, 3.25, 11,f[:-4], horizontalalignment='left', verticalalignment='bottom')
		# ax.set_zlim(0,10)
		# row_num = 6
		# col_num = 8
		# ticksx = np.arange(0, col_num, 1)
		# ticksy = np.arange(0, row_num, 1)
		# column_names = ['1','2','3','4','5','6','7','8']
		# row_names = ['1','2','3','4','5','6']
		# ax.xticks(ticksx, col_names)
		# ax.yticks(ticksy, row_names)

		if Exp_Des['Nozzle_Type'][f[:-4]] == 'Smooth Bore':
			Test_Name = str(Exp_Des['Tip_Size_(in)'][f[:-4]]) + '"' + ' ' + str(Exp_Des['Nozzle_Type'][f[:-4]]) + ' ' + str(Exp_Des['Location'][f[:-4]])
		elif Exp_Des['Nozzle_Type'][f[:-4]] == 'Fog' or 'Straight Stream':
			Test_Name = str(Exp_Des['Nozzle_Type'][f[:-4]]) + ' ' + str(Exp_Des['Location'][f[:-4]])

		Vents = Exp_Des['Vent_Configuration'][f[:-4]]
		Nozzle_Setting = str(int(Exp_Des['Flow_Rate_(gpm)'][f[:-4]]))+'gpm'+ ' ' + '@' + ' '+str(int(Exp_Des['Nozzle_Pressure_(psi)'][f[:-4]]))+'psi'
		Nozzle_Position = str(Exp_Des['Nozzle_Position'][f[:-4]])+ ','+' '+str(Exp_Des['Nozzle_Direction'][f[:-4]])
		Nozzle_Pattern = str(Exp_Des['Nozzle_Pattern'][f[:-4]])+' '+'Pattern'
		Hoseline_Size = str(Exp_Des['Hose_Line_Size'][f[:-4]])+'"'+' '+'Hose'

		print (Test_Name)

		row_num = 6
		col_num = 8
		ticksx = np.arange(0, col_num, 1)
		ticksy = np.arange(0, row_num, 1)
		column_names = ['1','2','3','4','5','6','7','8']
		row_names = ['1','2','3','4','5','6']

		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		# ax = Axes3D(plt.figure())
		ax.bar3d(X, Y, np.zeros(len(Zgraph)), dx, dy, Zgraph, zsort='max')
		ax.view_init(elev=48., azim=-160)
		# ax.text(5, 10, 14.85,Test_Name + ' ' + Nozzle_Setting, horizontalalignment='left', verticalalignment='bottom')
		ax.text(10, 3.25, 13,Test_Name, horizontalalignment='left', verticalalignment='bottom')
		ax.text(10, 3.25, 12,Hoseline_Size + ',' + ' ' + Nozzle_Setting, horizontalalignment='left', verticalalignment='bottom')
		# ax.text(10, 3.25, 11,Nozzle_Setting, horizontalalignment='left', verticalalignment='bottom')
		ax.text(10, 3.25, 11,Nozzle_Position, horizontalalignment='left', verticalalignment='bottom')
		ax.text(10, 3.25, 10,Nozzle_Pattern, horizontalalignment='left', verticalalignment='bottom')
		ax.text(10, 3.25, 9,Vents, horizontalalignment='left', verticalalignment='bottom')
		
		ax.set_zlim(0,10)
		ax.set_xlabel('Window Side (# of Bins)')
		ax.set_ylabel('Door Side (# of Bins)')
		ax.set_zlabel('Mass of Water Collected (kg)')
		# plt.xticks(ticksx, column_names)
		# plt.yticks(ticksy, row_names)

		# plt.show()

		plt.savefig('Figures/' + Test_Name.replace('/','_').replace('"','in') + Nozzle_Setting + Nozzle_Position + Nozzle_Pattern + '.png')
		plt.close('all')

# print len(X)
# print X

# print len(Z)
# print Z

# x = np.arange(-5,5,0.25)
# y = np.arange(-5,5,0.25)

# X,Y = np.meshgrid(x,y)

# Z = x**2 - Y**2

# print len(Z)
