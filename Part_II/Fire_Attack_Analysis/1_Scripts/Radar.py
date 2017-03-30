import numpy as np
import matplotlib.pyplot as plt
import pandas as pd 
import os
import re
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

def natural_keys(text):

    def atoi(text):
        return int(text) if text.isdigit() else text

    return [atoi(c) for c in re.split('(\d+)', text)]

def _radar_factory(num_vars):
    theta = 2*np.pi * np.linspace(0, 1-1./num_vars, num_vars)
    theta += np.pi/2

    def unit_poly_verts(theta):
        x0, y0, r = [0.5] * 3
        verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
        return verts

    class RadarAxes(PolarAxes):
        name = 'radar'
        RESOLUTION = 1

        def fill(self, *args, **kwargs):
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(theta * 180/np.pi, labels)

        def _gen_axes_patch(self):
            verts = unit_poly_verts(theta)
            return plt.Polygon(verts, closed=True, edgecolor='k')

        def _gen_axes_spines(self):
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            verts.append(verts[0])
            path = Path(verts)
            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta

def radar_graph(labels = [], values = pd.DataFrame(), ytitle = [], fill = []):
    N = len(labels) 
    theta = _radar_factory(N)

    fig = plt.figure(figsize=(20,15))
    ax = fig.add_subplot(1, 1, 1, projection='radar')
    
    values = values.reindex(columns=sorted(values.columns, key=natural_keys))

    for column in values.columns.values:
        ax.plot(theta, values[column], label=column[:-5].replace('_', ' '), lw=2)

    # Add the shaded area

    if fill == True:
        val_mean = data.mean(axis=1).tolist()

        shade_min = [val-(val*.15) for val in val_mean]
        shade_max = [val+(val*.15) for val in val_mean]

        ax.fill(theta, shade_max, color="#666666")
        ax.fill(theta, shade_min, color='white')

    ax.set_varlabels(labels)

    plt.legend(bbox_to_anchor=(-.3 , 1), loc=2, borderaxespad=0., fontsize=20)
    plt.yticks(fontsize=18)
    ax.get_xaxis().set_tick_params(direction='out')
    plt.xticks(fontsize=15)
    y_lim = ax.get_ylim()
    ax.text(.5,y_lim[1]*1.05, ytitle, fontsize = 20)
    ax.set_ylim(bottom=0)

# -------------------------------Plot the repeatibility plots and save-------------------------------
data_location = '../2_Data/'
events_location = '../3_Info/Events/'
output_location = '../0_Images/Results/Script_Figures/Repeatibility'
vent_info = pd.read_csv('../3_Info/Vent_Info.csv')

if not os.path.exists(output_location):
    os.makedirs(output_location)

for vent in vent_info.columns.values:
    repeatibility_data = pd.read_csv(data_location + '/Repeatibility_Data/' + vent + '.csv')
    
    for name, group in repeatibility_data.groupby('Type'):
        if name == 'Heat Flux':
            labels = [l.replace('_',' ') for l in group['Location']]
            ytitle = 'Heat Flux (kW/m2)'
        if name == 'Temperature': 
            labels = [l.replace('_',' ')[:-6] for l in group['Location']]
            ytitle = 'Temperature (F)'
       
        group = group.drop('Type', 1)
        data = group.drop('Location', 1)

        radar_graph(labels, data, ytitle, fill=True)

        plt.savefig(output_location + '/' + vent + '_' + name + '.pdf')
        plt.close('all')

# # -------------------------------Plot FED at Fire Department Intervention and save[NOT WORKING]-------------------------------
# data_location = '../2_Data/FED/'
# events_location = '../3_Info/Events/'
# output_location = '../0_Images/Results/Script_Figures/FED_Bar'
# FED_info = pd.read_csv('../3_Info/Vent_Info.csv')

# if not os.path.exists(output_location):
#     os.makedirs(output_location)

# data_files = ['Intervention_FED.csv', 'Intervention_Plus60_FED.csv', 'Intervention_FED_Temp.csv', 'Intervention_Plus60_FED_Temp.csv']
# # data_files = ['Intervention_FED_Temp.csv']

# for data_sets in data_files:
#     if not os.path.exists(output_location + '/' + data_sets[:-4]):
#         os.makedirs(output_location + '/' + data_sets[:-4])
    
#     FED_data = pd.read_csv(data_location+data_sets).set_index('Locations')
#     for vent in FED_info:
#         if 'Temp' in data_sets:
#             vics = ['FED_Temp_Vic1', 'FED_Temp_Vic2', 'FED_Temp_Vic3', 'FED_Temp_Vic4']
#             name = 'Temp'
#         else:
#             vics = ['FED_Vic1', 'FED_Vic2', 'FED_Vic3', 'FED_Vic4']
#             name = 'Gas'

#         exp_data = pd.DataFrame({'Locations':vics}).set_index('Locations')

#         for exp in FED_info[vent].dropna():

#             if exp not in FED_data:
#                 continue
                        
#             exp_data = pd.concat([exp_data, FED_data[exp]], axis = 1)
#         print (exp_data)
#         exit()
#         for vic in vics:

#             ytitle = 'Fractional Effective Dose'
#             labels = 
#             radar_graph(labels, data, ytitle, fill = False)
        
#         if '60' in data_sets:          
#             plt.savefig(output_location + '/' + vent + '_' + name + '_' +'_Plus60' + '.pdf')
#         else:
#             plt.savefig(output_location + '/' + vent + '_' + name + '_' + '.pdf')
#         plt.close('all')
