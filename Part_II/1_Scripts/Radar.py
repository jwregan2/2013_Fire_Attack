# ********************* Run Notes ***************************
# Must be run after the Build_Dictionary.py and Calculate_Repeatibility Data.py to create
# datafiles for the plots. 

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
output_location = '../0_Images/Script_Figures/Repeatibility'
vent_info = pd.read_csv('../3_Info/Vent_Info.csv')

if not os.path.exists(output_location):
    os.makedirs(output_location)

for vent in vent_info.columns.values:
    # print (vent)
    repeatibility_data = pd.read_csv(data_location + '/Repeatibility_Data/' + vent + '.csv')
    
    for exp in repeatibility_data:
        labels = [l.replace('_',' ')[:-6] for l in repeatibility_data['Location']]
        data = repeatibility_data.drop('Type', 1)
        data = data.drop('Location', 1)

        radar_graph(labels, data, 'Temperature F', fill=False)

        plt.savefig(output_location + '/' + vent + '.pdf')
        plt.close('all')
