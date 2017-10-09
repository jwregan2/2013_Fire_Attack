import matplotlib.pyplot as plt
import pandas as pd
import pickle

data_location = '../2_Data/'

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))


Plot TIC Data from Exp_12
tic_data = pd.read_csv(data_location + 'TIC_Data/Experiment_12_Data.csv').set_index('Time')

plt.plot(all_exp_data['Experiment_12_Data']['1TCV7'], label='7ft Temperature')
plt.plot(all_exp_data['Experiment_12_Data']['1TCV5'], label='5ft Temperature')
plt.plot(all_exp_data['Experiment_12_Data']['1TCV3'], label='3ft Temperature')
plt.plot(all_exp_data['Experiment_12_Data']['1TCV1'], label='1ft Temperature')
plt.plot(tic_data, label='Thermal Imaging Camera Temperature', color='black', lw=3)
plt.legend()
plt.xlim([208,264])
plt.ylim([0,800])
plt.xlabel('Time (Seconds)', fontsize=14)
plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
plt.savefig('../0_Images/Script_Figures/TIC.png')
exit()