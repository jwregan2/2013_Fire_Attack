import pandas as pd 
import os as os
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
import datetime
from dateutil.relativedelta import relativedelta
from itertools import cycle

# Set file locations

data_location = '../Experimental_Data/'

chart_location = '../../Report/Script_Figures/Entrainment/'

info_file = '../Info/description_of_experiments_entrainment.csv'
plot_file = '../Info/description_of_charts.csv'

# Read in description of experiments
Exp_Des = pd.read_csv(info_file)
Exp_Des = Exp_Des.set_index('Test_Name')
# Set files to skip in experimental directory
skip_files = ['_events']

channels_nr = ['BDP1V','BDP2V','BDP3V','BDP4V','BDP5V']
channels_nr2 = ['BDP1VLR','BDP2VLR','BDP3VLR','BDP4VLR','BDP5VLR']
channels_hr = ['BDP1VHR','BDP2VHR','BDP3VHR','BDP4VHR','BDP5VHR']
channels_matrix_hr = ['Matrix1VHR','Matrix2VHR','Matrix3VHR','Matrix4VHR','Matrix5VHR']
channels_matrix_lr = ['Matrix1VLR','Matrix2VLR','Matrix3VLR','Matrix4VLR','Matrix5VLR']


# Loop through Experiment files
for f in os.listdir(data_location):
	if f.endswith('.csv'):

		# Skip files with time information or reduced data files
		if any([substring in f.lower() for substring in skip_files]):
			continue

		# Read in experiment file
		experiment = f

		# exp = experiment[11:-9]
		Exp_Data = pd.read_csv(data_location + experiment)
		data_copy = Exp_Data.drop('Elapsed Time', axis=1)
		data_copy = data_copy.rolling(window=1, center=True).mean()
		data_copy.insert(0, 'Elapsed Time', Exp_Data['Elapsed Time'])
		data_copy = data_copy.dropna()
		Exp_Data = data_copy

		Exp_Events = pd.read_csv(data_location + experiment[:-4]+'_Events.csv')
		Event_Time = [datetime.datetime.strptime(t, '%Y-%m-%d-%H:%M:%S') for t in Exp_Events['Time']]

		# Get experiment name from file
		Test_Name = experiment[:-4]
		Exp_Num = Test_Name[4:-7]

		if Exp_Des['Test_Config'][Test_Name] == 'ignore':
			continue

		temp_time = []
		for i in range(len(Event_Time)):
			temp_time.append(Event_Time[i].timestamp() - Event_Time[0].timestamp())
		Exp_Events['Elapsed_Time'] = temp_time
		Start_Time = Exp_Events['Elapsed_Time'][0]
		End_Time = temp_time[-1]

		BDP_Resolution = Exp_Des['BDP_Res'][Test_Name]
		if BDP_Resolution == 'N':
			if int(Exp_Num) < 43:
				channels = channels_nr
			else:
				channels = channels_nr2
			conv_inch_h2o = 0.04
		elif BDP_Resolution == 'M':
			channels = channels_matrix_hr
			conv_inch_h2o = 0.2
		elif BDP_Resolution == 'ML':
			channels = channels_matrix_lr
			conv_inch_h2o = 0.04
		else:
			channels = channels_hr
			conv_inch_h2o = 0.2

		print (Test_Name)

		area = 17.778
		for channel in channels:
			#Calculate velocity
			conv_pascal = 248.84
			convert_ftpm = 196.85
			end_zero_time = int(Exp_Events['Elapsed_Time'][1])
			zero_voltage = np.mean(Exp_Data[channel][0:end_zero_time])
			pressure = conv_inch_h2o * conv_pascal * (Exp_Data[channel]-zero_voltage)  # Convert voltage to pascals
			# Calculate flowrate
			Exp_Data[channel] = convert_ftpm * 0.0698 * np.sqrt(np.abs(pressure) * ((Exp_Des['Temp_C'][Test_Name])+273.13)) * np.sign(pressure)

		#Calculate cfm
		if int(Exp_Num) < 25:
			CFM = area*(Exp_Data[[channels[0],channels[2],channels[3]]].mean(axis=1))
			CFM_1 = area*(Exp_Data[channels[2]])
			CFM_3 = area*(Exp_Data[[channels[2],channels[3]]].mean(axis=1))
		else:
			CFM = area*np.mean(Exp_Data[channels],axis=1)
			CFM_1 = area*(Exp_Data[channels[2]])
			CFM_3 = area*np.mean(Exp_Data[channels[1:3]],axis=1)
		zero_CFM = np.mean(CFM[0:end_zero_time])
		zero_CFM_1 = np.mean(CFM_1[0:end_zero_time])
		zero_CFM_3 = np.mean(CFM_3[0:end_zero_time])
		CFM = CFM - zero_CFM
		CFM_1 = CFM_1 - zero_CFM_1
		CFM_3 = CFM_3 - zero_CFM_3
		cfm_avgs = []
		for i in range(1,len(Exp_Events)):
			pos2 = int(Exp_Events['Elapsed_Time'][i])
			pos1 = int(Exp_Events['Elapsed_Time'][i-1])
			cfm_avgs.append(np.mean(CFM[pos1:pos2]))
		cfm_avgs = np.append(cfm_avgs,0)
		Exp_Events['CFM_Avg'] = cfm_avgs
		Exp_Events.to_csv('../Experimental_Data/'+ Test_Name + '_Events_CFM.csv')
		time = list(range(len(Exp_Data)))

		# fig = figure()
		# plt.plot(time,CFM,'r--',linewidth=1.5)
		# # plt.plot(time,CFM_3,'b--',label='CFM Middle 3')
		# # plt.plot(time,CFM_1,'r-.',label='CFM Middle')
		# for i in range(1,len(Exp_Events)):
		# 	plt.plot([Exp_Events['Elapsed_Time'][i-1],Exp_Events['Elapsed_Time'][i]],[cfm_avgs[i-1],cfm_avgs[i-1]],color='black',linewidth=2)
		# ax1 = plt.gca()
		# handles1, labels1 = ax1.get_legend_handles_labels()
		# ax1.xaxis.set_major_locator(plt.MaxNLocator(8))
		# ax1_xlims = ax1.axis()[0:2]
		# plt.xlim([0, End_Time-Start_Time])
		# plt.xlabel('Time (s)')
		# plt.ylabel('CFM (ft$^3$/min)')
		# try:
		# 	# Add vertical lines and labels for timing information (if available)
		# 	ax3 = ax1.twiny()
		# 	ax3.set_xlim(ax1_xlims)
		# 	# Remove NaN items from event timeline
		# 	events = Exp_Events['Event']
		# 	[plt.axvline(_x, color='0.50', lw=1) for _x in Exp_Events['Elapsed_Time']]
		# 	ax3.set_xticks(Exp_Events['Elapsed_Time'])
		# 	plt.setp(plt.xticks()[1], rotation=40)
		# 	ax3.set_xticklabels(events.values, fontsize=8, ha='left')
		# 	plt.xlim([0, End_Time])
		# 	# Increase figure size for plot labels at top
		# 	fig.set_size_inches(10, 9)
		# except:
		# 	pass
		# # plt.legend(handles1, labels1, loc='upper left', fontsize=12, handlelength=3)
		# savefig(chart_location+Test_Name+'_CFM.pdf')
		# close()

tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(tableau20)):
    r, g, b = tableau20[i]
    tableau20[i] = (r / 255., g / 255., b / 255.)

# Plotting
plot_file = pd.read_csv(plot_file)
for k in range(len(plot_file)):
	if plot_file['Chart_Status'][k] == 'ignore':
		continue
	print('Plotting: ' + plot_file['Plot_Name'][k])
	test_comps=[]
	event_nums=[]
	legend_names = []
	event_nums_anomoly = []
	temp1 = plot_file['Experiments_To_Compare'][k].split('|')
	test_comps = np.asarray(temp1)
	if plot_file['Anomalies'][k] == 0:
		temp2 = plot_file['Bars'][k].split('|')
		event_nums = np.asarray(temp2)
	elif plot_file['Anomalies'][k] == 1:
		temp2 = plot_file['Bars'][k].split('|')
		event_nums = np.asarray(temp2)
		temp3 = plot_file['New_Bars'][k].split('|')
		event_nums_anomaly = np.asarray(temp3)
		temp4 = plot_file['Anomaly_Exp'][k].split('|')
		test_anomaly = np.asarray(temp4)
	temp5 = plot_file['Legend'][k].split('|')
	legend_names = np.asarray(temp5)
	file_name = plot_file['Plot_Name'][k]

	ind = np.arange(len(event_nums))  # the x locations for the groups
	width = 0.8/len(test_comps)  # the width of the bars

	# fig, ax = plt.subplots(figsize=(10, 9))
	# cfm_bars = np.zeros((len(test_comps),len(event_nums)))
	# labels = ["" for x in range(len(event_nums))]
	# for i in range(len(test_comps)):
	# 	temp_read = pd.read_csv('../Experimental_Data/'+test_comps[i]+'_Events_CFM.csv')
	# 	for j in range(len(event_nums)):
	# 		if plot_file['Anomalies'][k] == 0:
	# 			cfm_bars[i,j] = temp_read['CFM_Avg'][int(event_nums[j])]
	# 			labels[j] = temp_read['Event'][int(event_nums[j])]
	# 		elif plot_file['Anomalies'][k] == 1:
	# 			if test_comps[i] in test_anomaly[:]:
	# 				cfm_bars[i,j] = temp_read['CFM_Avg'][int(event_nums_anomaly[j])]
	# 			else:
	# 				cfm_bars[i,j] = temp_read['CFM_Avg'][int(event_nums[j])]
	# 				labels[j] = temp_read['Event'][int(event_nums[j])]
	# 	uncert = 0.18*cfm_bars[i,:]
	# 	rects = ax.bar(ind+i*width, cfm_bars[i,:], width, color=tableau20[i],yerr=uncert,error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))

	# # box = ax.get_position()
	# # ax.set_position([box.x0, box.y0, box.width * 0.7, box.height])
	# # ax.legend(legend_names,loc=plot_file['Legend_Location'][k], bbox_to_anchor=(1, 0.5))
	# ax.legend(legend_names,loc=plot_file['Legend_Location'][k],fontsize=16)
	# # ax.set_title(plot_file['Chart_Title'][k])
	# ax.set_ylabel('Average CFM (ft$^3$/min)', fontsize=18)
	# if len(test_comps) == 1:
	# 	ax.set_xticks(ind + width/2)
	# else:
	# 	ax.set_xticks(ind + width)
	# ax.set_xticklabels(labels, rotation = -15, ha = 'left',fontsize=16)
	# ax.tick_params(axis='both', which='major', labelsize=16)
	# # max_y = max(zip(cfm_bars[i,:], uncert))
	# # plt.ylim([0, (max_y[0] + max_y[1]) * 1.1])
	# ylim([plot_file['Min'][k],plot_file['Max'][k]])
	# savefig(chart_location+file_name+'.pdf')
	# plt.close('all')


#-----------------------
# One off plots
#-----------------------

exp04 = pd.read_csv('../Experimental_Data/Exp_04_102615_Events_CFM.csv')
exp05 = pd.read_csv('../Experimental_Data/Exp_05_102615_Events_CFM.csv')
exp06 = pd.read_csv('../Experimental_Data/Exp_06_102615_Events_CFM.csv')
exp07 = pd.read_csv('../Experimental_Data/Exp_07_102615_Events_CFM.csv')
exp08 = pd.read_csv('../Experimental_Data/Exp_08_102615_Events_CFM.csv')
exp09 = pd.read_csv('../Experimental_Data/Exp_09_102615_Events_CFM.csv')
exp10 = pd.read_csv('../Experimental_Data/Exp_10_102615_Events_CFM.csv')
exp11 = pd.read_csv('../Experimental_Data/Exp_11_102615_Events_CFM.csv')
exp12 = pd.read_csv('../Experimental_Data/Exp_12_102615_Events_CFM.csv')
exp13 = pd.read_csv('../Experimental_Data/Exp_13_102615_Events_CFM.csv')
exp14 = pd.read_csv('../Experimental_Data/Exp_14_102615_Events_CFM.csv')
exp15 = pd.read_csv('../Experimental_Data/Exp_15_102615_Events_CFM.csv')
exp16 = pd.read_csv('../Experimental_Data/Exp_16_102615_Events_CFM.csv')
exp17 = pd.read_csv('../Experimental_Data/Exp_17_102615_Events_CFM.csv')
exp18 = pd.read_csv('../Experimental_Data/Exp_18_102715_Events_CFM.csv')
exp19 = pd.read_csv('../Experimental_Data/Exp_19_102715_Events_CFM.csv')
exp20 = pd.read_csv('../Experimental_Data/Exp_20_102715_Events_CFM.csv')
exp21 = pd.read_csv('../Experimental_Data/Exp_21_102715_Events_CFM.csv')
exp22 = pd.read_csv('../Experimental_Data/Exp_22_102715_Events_CFM.csv')
exp23 = pd.read_csv('../Experimental_Data/Exp_23_102715_Events_CFM.csv')
exp24 = pd.read_csv('../Experimental_Data/Exp_24_102715_Events_CFM.csv')

mean_values = [exp08['CFM_Avg'][1],exp04['CFM_Avg'][1],exp04['CFM_Avg'][5]]
variance = [0.18*exp08['CFM_Avg'][1],0.18*exp04['CFM_Avg'][1],0.18*exp04['CFM_Avg'][5]]
bar_labels = [exp08['Event'][1],exp04['Event'][1],exp04['Event'][5]]
x_pos = list(range(len(bar_labels)))
fig, ax = plt.subplots(figsize=(10, 9))
plt.bar(x_pos, mean_values, yerr=variance, align='center', color=tableau20[0],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
max_y = max(zip(mean_values, variance))
plt.ylim([0, (max_y[0] + max_y[1]) * 1.1])
plt.ylabel('Average CFM (ft$^3$/min)', fontsize=18)
plt.xticks(x_pos, bar_labels,rotation = -15)
ax.tick_params(axis='both', which='major', labelsize=16)
plt.legend(['150 gpm @ 50 psi'], loc='upper left')
savefig(chart_location+'Hosestream_Type_1_5_int'+'.pdf')

mean_values = [exp08['CFM_Avg'][2],exp04['CFM_Avg'][2],exp04['CFM_Avg'][6]]
variance = [0.18*exp08['CFM_Avg'][2],0.18*exp04['CFM_Avg'][2],0.18*exp04['CFM_Avg'][6]]
bar_labels = [exp08['Event'][2],exp04['Event'][2],exp04['Event'][6]]
x_pos = list(range(len(bar_labels)))
fig, ax = plt.subplots(figsize=(10, 9))
plt.bar(x_pos, mean_values, yerr=variance, align='center', color=tableau20[0],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
max_y = max(zip(mean_values, variance))
plt.ylim([0, (max_y[0] + max_y[1]) * 1.1])
plt.ylabel('Average CFM (ft$^3$/min)', fontsize=18)
plt.xticks(x_pos, bar_labels,rotation = -15)
ax.tick_params(axis='both', which='major', labelsize=16)
plt.legend(['150 gpm @ 50 psi'], loc='upper left')
savefig(chart_location+'Hosestream_Type_1_5_int_move'+'.pdf')

mean_values_MFI   = [exp04['CFM_Avg'][1],exp08['CFM_Avg'][1]] 
variance_MFI      = [0.18*exp04['CFM_Avg'][1],0.18*exp08['CFM_Avg'][1]] 
mean_values_MFII  = [exp18['CFM_Avg'][1],exp22['CFM_Avg'][1]] 
variance_MFII     = [0.18*exp18['CFM_Avg'][1],0.18*exp22['CFM_Avg'][1]] 
mean_values_MFIII = [exp11['CFM_Avg'][1],exp15['CFM_Avg'][1]] 
variance_MFIII    = [0.18*exp11['CFM_Avg'][1],0.18*exp15['CFM_Avg'][1]] 

bar_labels = [exp04['Event'][1],exp08['Event'][1]]
x_pos = list(range(len(bar_labels)))
width = 0.25
fig, ax = plt.subplots(figsize=(10, 9))
plt.bar([p - width for p in x_pos], mean_values_MFI, width, yerr=variance_MFI, align='center', color=tableau20[0],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
plt.bar([p for p in x_pos], mean_values_MFII, width,yerr=variance_MFII, align='center', color=tableau20[1],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
plt.bar([p + width for p in x_pos], mean_values_MFIII, width, yerr=variance_MFIII, align='center', color=tableau20[2],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
max_y = max(zip(mean_values_MFII, variance))
plt.ylim([0, (max_y[0] + max_y[1]) * 1.1])
plt.ylabel('Average CFM (ft$^3$/min)', fontsize=18)
plt.xticks([p for p in x_pos], bar_labels,rotation = -15)
ax.tick_params(axis='both', which='major', labelsize=16)
plt.legend(['MFI','MFII','MFIII'], loc='upper left')
savefig(chart_location+'SS_SB_Manufacture'+'.pdf')


mean_values_MFI   = [exp04['CFM_Avg'][1],exp05['CFM_Avg'][1],exp06['CFM_Avg'][1],exp07['CFM_Avg'][1],exp08['CFM_Avg'][1],exp09['CFM_Avg'][1],exp10['CFM_Avg'][1]] 
variance_MFI      = 0.18*np.asarray(mean_values_MFI)
mean_values_MFII  = [exp21['CFM_Avg'][1],exp20['CFM_Avg'][1],exp18['CFM_Avg'][1],exp19['CFM_Avg'][1],exp22['CFM_Avg'][1],exp23['CFM_Avg'][1],exp24['CFM_Avg'][1]] 
variance_MFII     = 0.18*np.asarray(mean_values_MFII)
mean_values_MFIII = [exp14['CFM_Avg'][1],exp13['CFM_Avg'][1],exp11['CFM_Avg'][1],exp12['CFM_Avg'][1],exp15['CFM_Avg'][1],exp16['CFM_Avg'][1],exp17['CFM_Avg'][1]] 
variance_MFIII    = 0.18*np.asarray(mean_values_MFIII)

bar_labels = ['150 gpm @ 50 psi','150 gpm @ 75 psi','150 gpm @ 100 psi','95 gpm @ 100 psi','150 gpm @ 50 psi','180 gpm @ 50 psi','210 gpm @ 50 psi']
# bar_labels = [exp04['Event'][1],exp05['Event'][1],exp06['Event'][1],exp07['Event'][1],exp08['Event'][1],exp09['Event'][1],exp10['Event'][1]]
x_pos = list(range(len(bar_labels)))
width = 0.25
fig, ax = plt.subplots(figsize=(12, 8))
plt.bar([p - width for p in x_pos], mean_values_MFI, width, yerr=variance_MFI, align='center', color=tableau20[0],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
plt.bar([p for p in x_pos], mean_values_MFII, width,yerr=variance_MFII, align='center', color=tableau20[1],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
plt.bar([p + width for p in x_pos], mean_values_MFIII, width, yerr=variance_MFIII, align='center', color=tableau20[2],error_kw=dict(ecolor='black', lw=1.5, capsize=4, capthick=1.5))
max_y = max(zip(mean_values_MFII, variance))
plt.ylim([0, (max_y[0] + max_y[1]) * 1.1])
plt.ylabel('Average CFM (ft$^3$/min)', fontsize=18)
plt.xticks([p for p in x_pos], bar_labels, ha='left', rotation = -30)
ax.tick_params(axis='both', which='major', labelsize=16)
plt.legend(['MFI','MFII','MFIII'], loc='upper left')
fig.tight_layout()
savefig(chart_location+'All_SS_SB_Manufacture'+'.pdf')

