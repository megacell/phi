from django.db import connection
from django_utils import config
import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.io as sio

def total_flow():
    cursor = connection.cursor()
    cursor.execute('''
    select sum(flow_count) from experiment2_routes''')
    return cursor.fetchone()[0]

def total_captured_trajectories(maximum_routes_per_od):
    cursor = connection.cursor()
    cursor.execute('''
    select sum(flow_count) from experiment2_routes where od_route_index < %s;
    ''', (maximum_routes_per_od,))
    return cursor.fetchone()[0]

def export_route_stats(output_file):
    output = {'total_flow':total_flow(),
            'similarity_factor':config.SIMILARITY_FACTOR,
            'captured_flow':[total_captured_trajectories(i) for i in range(1,101)]}
    sio.savemat(output_file, output)

def plot_route_vs_trajectories():
    x = list(range(1,101))
    t = float(total_flow())
    y = [total_captured_trajectories(i)/t for i in x]
    print t, x, y
    plt.plot(x,y,'o')
    plt.title('Routes vs Percent of Total Flow')
    plt.xlabel('Maximum Routes per (o, d)')
    plt.ylabel('Percent of Total Flow Represented')
    plt.show()

if __name__ == "__main__":
    export_route_stats(config.PLOT_DIR+ '/modeled_flow.mat')
    plot_route_vs_trajectories()