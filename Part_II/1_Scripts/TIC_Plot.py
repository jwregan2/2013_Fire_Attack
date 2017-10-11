import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os

data_location = '../2_Data/'

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

output_location = '../0_Images/Script_Figures/Experiment_Analysis/Thermal_Imaging_Camera/'

# If the folder doesn't exist create it.
if not os.path.exists(output_location):
	os.makedirs(output_location)

# Plot TIC Data from Exp_12
tic_data = pd.read_csv(data_location + 'TIC_Data/Experiment_12_Data_2.csv').set_index('Time')

plt.plot(all_exp_data['Experiment_12_Data']['1TCV7'], label='7ft Temperature')
plt.plot(all_exp_data['Experiment_12_Data']['1TCV5'], label='5ft Temperature')
plt.plot(all_exp_data['Experiment_12_Data']['1TCV3'], label='3ft Temperature')
plt.plot(all_exp_data['Experiment_12_Data']['1TCV1'], label='1ft Temperature')
plt.plot(tic_data, ['Hall IR'], label='Hall Thermal Imaging Camera Temperature', color='black', lw=3)
plt.plot(tic_data, ['Front Door IR'], label='Front Door Thermal Imaging Camera Temperature', color='blue', lw=3)
plt.legend()
plt.xlim([208,264])
plt.ylim([0,800])
plt.xlabel('Time (Seconds)', fontsize=14)
plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
plt.savefig('../0_Images/Script_Figures/TIC_12.png')

# Plot TIC Data from Exp_1
tic_data = pd.read_csv(data_location + 'TIC_Data/Experiment_1_Data.csv').set_index('Time')

plt.plot(all_exp_data['Experiment_1_Data']['1TCV7'], label='7ft Temperature')
plt.plot(all_exp_data['Experiment_1_Data']['1TCV5'], label='5ft Temperature')
plt.plot(all_exp_data['Experiment_1_Data']['1TCV3'], label='3ft Temperature')
plt.plot(all_exp_data['Experiment_1_Data']['1TCV1'], label='1ft Temperature')
plt.plot(tic_data, label='Thermal Imaging Camera Temperature', color='black', lw=3)
plt.legend()
plt.xlim([0,450])
plt.ylim([0,200])
plt.xlabel('Time (Seconds)', fontsize=14)
plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
plt.savefig('../0_Images/Script_Figures/TIC_1.png')

# Plot TIC Data from Exp_17
tic_data = pd.read_csv(data_location + 'TIC_Data/Experiment_17_Data.csv').set_index('Time')

plt.plot(all_exp_data['Experiment_17_Data']['1TCV7'], label='7ft Temperature')
plt.plot(all_exp_data['Experiment_17_Data']['1TCV5'], label='5ft Temperature')
plt.plot(all_exp_data['Experiment_17_Data']['1TCV3'], label='3ft Temperature')
plt.plot(all_exp_data['Experiment_17_Data']['1TCV1'], label='1ft Temperature')
plt.plot(tic_data, label='Thermal Imaging Camera Temperature', color='black', lw=3)
plt.legend()
plt.xlim([0,450])
plt.ylim([0,200])
plt.xlabel('Time (Seconds)', fontsize=14)
plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
plt.savefig('../0_Images/Script_Figures/TIC_17.png')

# Plot TIC Data from Exp_19
tic_data = pd.read_csv(data_location + 'TIC_Data/Experiment_19_Data.csv').set_index('Time')

plt.plot(all_exp_data['Experiment_19_Data']['1TCV7'], label='7ft Temperature')
plt.plot(all_exp_data['Experiment_19_Data']['1TCV5'], label='5ft Temperature')
plt.plot(all_exp_data['Experiment_19_Data']['1TCV3'], label='3ft Temperature')
plt.plot(all_exp_data['Experiment_19_Data']['1TCV1'], label='1ft Temperature')
plt.plot(tic_data, label='Thermal Imaging Camera Temperature', color='black', lw=3)
plt.legend()
plt.xlim([0,450])
plt.ylim([0,200])
plt.xlabel('Time (Seconds)', fontsize=14)
plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
plt.savefig('../0_Images/Script_Figures/TIC_9.png')
exit()