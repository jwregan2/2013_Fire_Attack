# Import pandas library as pd
import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle

#Read data file 'Example_Data.csv' from down one directory and into 2_Data.
data = pd.read_csv('../2_Data/Example_Data.csv')

# Print first five rows of data
print('Original Data')
print(data.head()) 

# #loop through each column of the data and convert to F if not 'Time'
# for channel in data:
# 	if 'TC' in channel:
# 		data[channel] = data[channel] * 1.8 + 32
# 	elif 'HF' in channel:
# 		continue
# 	elif 'BDP' in channel:
# 		continue
# 	elif 'Press' in channel:
# 		continue
# 	elif 'Time' in channel:
# 		data[channel] = data[channel] / 60
# 	else:
# 		print('Channel', channel, 'Not Converted')

# Print first five rows of converted data
print('Converted Data')
print(data.head()) 

#Creating a blank figure
fig = plt.figure()

marker_style = cycle(['x','o','s','v'])

for channel in data:
	if 'TC' in channel:
		plt.plot(data['Time'],data[channel] * 1.8 + 32, label=channel, marker=next(marker_style), markevery=5)

# #Print 1TC1 with label of 1TC1
# plt.plot(data['Time'],data['1TC1'], label = '1TC1', marker = '*')
# plt.plot(data['Time'],data['1TC3'], label = '1TC3', marker = 'x')
# plt.plot(data['Time'],data['1TC5'], label = '1TC5', marker = 'v')
# plt.plot(data['Time'],data['1TC7'], label = '1TC7', marker = 'o')

plt.legend(loc='upper left', fontsize=16, numpoints=1)
plt.xlabel('Time', fontsize = 16)
plt.ylabel('Temperature $^{\circ}$F', fontsize = 16)
plt.title('Bedroom 1 Temperature', fontsize = 20)
plt.xlim([0,32])
plt.ylim([0,2000])

plt.show()

# plt.savefig('../0_Images/Results/Bedroom1Temp.pdf')