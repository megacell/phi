__author__ = 'lei'
from django.db import connection
from matplotlib import pyplot as plt
import numpy as np
class ReduceRouteCounter:
    def __init__(self):
        self.routes = ReduceRouteCounter.get_routes()
        self.typemap = ReduceRouteCounter.get_type_map()
    @staticmethod
    def get_routes():
        sql_query = '''select links from experiment2_routes'''#experiment2_trajectories;'''
        cursor = connection.cursor()
        cursor.execute(sql_query)
        return [links for links, in cursor]

    @staticmethod
    def get_type_map():
        sql_query = '''
            select link_id, type from link_id_type;
            '''

        cursor = connection.cursor()

        cursor.execute(sql_query)

        typemap = {k:v for k,v in cursor}
        return typemap

    @staticmethod
    def filter_links(links, types, typemap):
        return [link for link in links if typemap[link] in types]

    def count_routes(self, typeset):
        routes = self.routes
        typemap = self.typemap
        filtered_links = [ReduceRouteCounter.filter_links(links, typeset, typemap) for links in routes]
        route_set = set()
        for links in filtered_links:
            route_set.add(tuple(links))
        return len(route_set)
def plot_reducedroutes():
    types = [u'"motorway"',
     u'"motorway_link"',
     u'"primary"',
     u'"primary_link"',
     u'"trunk"',
     u'"trunk_link"',
     u'"secondary"',
     u'"unclassified"',
     u'"tertiary"',
     u'"living_street"']
    rrc = ReduceRouteCounter()
    typeset = set()
    counts = []
    for type in types:
        typeset.add(type)
        counts.append(rrc.count_routes(typeset))
        print counts
    print len(rrc.routes)
    N = len(counts)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    plt.bar(ind, counts, width)

    plt.ylabel('Trajectory Count')
    plt.title('Cumulative Trajectory Usage')

    plt.xticks(ind+width/2., [i.strip('"') for i in types])
    plt.show()

plot_reducedroutes()