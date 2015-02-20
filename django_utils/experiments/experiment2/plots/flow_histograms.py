__author__ = 'lei'
from django.db import connection
from django_utils import config
import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.io as sio
from collections import defaultdict
def plot_route_flow():
    sql = '''select flow_count from experiment2_routes;'''
    cursor = connection.cursor()
    cursor.execute(sql)
    x = [i for i, in cursor]
    plt.hist(x,bins=50, range=(1,50))
    plt.xlabel("Flow")
    plt.ylabel("Number of routes")
    plt.show()

class LinkAgg:
    def __init__(self):
        self.link_flows = defaultdict(lambda: 0)

    def add(self, flow_count, links):
        for i in links:
            self.link_flows[i] += flow_count

    def get_flows(self):
        return self.link_flows.values()

def plot_link_flow():
    sql = '''select flow_count, r.links from experiment2_routes r;'''
    cursor = connection.cursor()
    cursor.execute(sql)
    la = LinkAgg()
    for flow, links in cursor:
        la.add(flow, links)

    plt.hist(la.get_flows() ,bins=100, range=(0,10000))
    plt.xlabel("Flow")
    plt.ylabel("Number of links")
    plt.show()

plot_route_flow()
plot_link_flow()