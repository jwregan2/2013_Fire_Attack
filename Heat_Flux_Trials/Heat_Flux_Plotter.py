import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle

data = pd.read_csv('Heatfluxtest.csv')

#Creating a blank figure
fig = plt.figure()

marker_style = cycle(['x','o'])

for channel in data:
	if 'Voltage' in channel:
		plt.plot(data['Elapsed Time'],data[channel] * 1.919, label=channel, marker=next(marker_style), markevery=5)

plt.legend(loc='upper left', fontsize=16, numpoints=1)
plt.xlabel('Time (sec)', fontsize = 16)
plt.ylabel('Heat Flux kW/m^2', fontsize = 16)
plt.title('Heat Flux Trials', fontsize = 20)
plt.xlim([0,1000])
plt.ylim([0,20])

# plt.show()

plt.savefig('HeatFluxTrials.pdf')