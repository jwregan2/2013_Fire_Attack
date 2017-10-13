import matplotlib.pyplot as plt
import pandas as pd
import pickle
import os

data_location = '../2_Data/'

tic_location = '../2_Data/TIC_Data/'

all_exp_data = pickle.load(open(data_location + 'all_exp_data.dict', 'rb'))

output_location = '../0_Images/Script_Figures/Experiment_Analysis/Thermal_Imaging_Camera/'

end_time={'Experiment_1':418, 'Experiment_12':326, 'Experiment_17':324, 'Experiment_19':574}
end_temp_hall={'Experiment_1':700, 'Experiment_12':700, 'Experiment_17':1700, 'Experiment_19':1200}
end_temp_door={'Experiment_1':400, 'Experiment_12':400, 'Experiment_17':600, 'Experiment_19':600}

# If the folder doesn't exist create it.
if not os.path.exists(output_location):
	os.makedirs(output_location)

# establish new variable 
experiments = ['Experiment_1', 'Experiment_12', 'Experiment_17', 'Experiment_19']

for exp in experiments:
	
# Plot TIC Data for Hall IR
	print (tic_location + exp + '_Data.csv')
	tic_data = pd.read_csv(tic_location + exp + '_Data.csv').set_index('Time')

	plt.plot(all_exp_data[exp + '_Data']['1TCV7'], label='7ft Temperature')
	plt.plot(all_exp_data[exp + '_Data']['1TCV5'], label='5ft Temperature')
	plt.plot(all_exp_data[exp + '_Data']['1TCV3'], label='3ft Temperature')
	plt.plot(all_exp_data[exp + '_Data']['1TCV1'], label='1ft Temperature')
	plt.plot(tic_data['Hall'], label='Hall Thermal Imaging Camera Temperature', color='black', lw=3)
	plt.legend()
	plt.xlim([0,end_time[exp]])
	plt.ylim([0,end_temp_hall[exp]])
	plt.xlabel('Time (Seconds)', fontsize=14)
	plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
	plt.savefig(output_location + exp + '_Hall.png')
	plt.close()

# Plot TIC Data for Front Door IR
	plt.plot(all_exp_data[exp + '_Data']['4TCV7'], label='7ft Temperature')
	plt.plot(all_exp_data[exp + '_Data']['4TCV5'], label='5ft Temperature')
	plt.plot(all_exp_data[exp + '_Data']['4TCV3'], label='3ft Temperature')
	plt.plot(all_exp_data[exp + '_Data']['4TCV1'], label='1ft Temperature')
	plt.plot(tic_data['Front'], label='Front Door Thermal Imaging Camera Temperature', color='black', lw=3)
	plt.legend()
	plt.xlim([0,end_time[exp]])
	plt.ylim([0,end_temp_door[exp]])
	plt.xlabel('Time (Seconds)', fontsize=14)
	plt.ylabel('Temperature ($^\circ$F)', fontsize=14)
	plt.savefig(output_location + exp +'_Door.png')
	plt.close()

exit()