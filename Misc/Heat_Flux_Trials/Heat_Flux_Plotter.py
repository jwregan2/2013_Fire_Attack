import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import HoverTool

data = pd.read_csv('Heatfluxtest2.csv')

#Creating a blank figure
fig = plt.figure()

marker_style = cycle(['x','o'])

# #Set Tools for Bokeh Plots
# TOOLS = 'box_zoom,reset,hover,pan,wheel_zoom'

# # Create figure with set x-axis, set size, and available tools in bokeh package
# output_file('HeatFluxtest2.html')
# p = figure( x_axis_label='Time(min)', tools=TOOLS, height=500, width=1200 )


for channel in data:
	if 'Voltage' in channel:
		plt.plot(data['Elapsed Time'],data[channel] * 1.919, label=channel, marker=next(marker_style), markevery=5)
# 		p.line(data['Elapsed Time'], data[channel]*1.919)

# save(p)

plt.legend(loc='upper left', fontsize=16, numpoints=1)
plt.xlabel('Time (sec)', fontsize = 16)
plt.ylabel('Heat Flux kW/m^2', fontsize = 16)
plt.title('Heat Flux Trials', fontsize = 20)
# plt.xlim([0,1000])
plt.ylim([0,25])

# plt.show()

plt.savefig('HeatFluxTrials2.pdf')