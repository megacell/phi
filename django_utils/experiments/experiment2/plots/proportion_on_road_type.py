__author__ = 'lei'

from django.db import connection
from matplotlib import pyplot as plt
from django.contrib.gis.geos import GEOSGeometry
import math
import numpy as np

def get_link_length_map():
    sql_query = "SELECT link_id, geom_dist FROM link_geometry;"
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        return {id:GEOSGeometry(geom).length for id, geom in cursor}

def get_trajectories():
    sql_query = '''select link_ids from experiment2_trajectories;'''
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        return [links for links, in cursor]

def get_link_type_map():
    sql_query = '''select link_id, type from link_id_type;'''
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        return {id:type for id, type in cursor}

def total_length(links, length_map):
    return sum(length_map[link] for link in links)

def has_type(links, link_type_map, type):
    for link in links:
        if link_type_map[link] == type:
            return True
    return False

def has_types(links, link_type_map, types):
    for link in links:
        if link_type_map[link] in types:
            return True
    return False


class Buckets:
    def __init__(self,a,b,n):
        self.a = a
        self.b = b
        self.n = n
        self.buckets = [0]*n

    def add(self, x):
        binsize = (self.b-self.a)/float(self.n)
        index = int(math.floor((x-self.a)/binsize))
        if 0 <= index < self.n:
            self.buckets[index] += 1
    def range(self):
        return np.linspace(self.a, self.b, self.n)
    def update(self, xs):
        for x in xs:
            self.add(x)

class TypeHist:
    def __init__(self):
        self.link_type_map = get_link_type_map()
        self.link_length = get_link_length_map()

        self.trajectories = get_trajectories()
        self.types = set()
    def set_types(self,types):
        self.types = set(types)

    def plot_hist(self, title):
        link_type_map = self.link_type_map
        link_length = self.link_length

        trajectories = self.trajectories
        interesting = filter(lambda links: has_types(links, link_type_map, self.types), trajectories)
        not_interesting = filter(lambda links: not has_types(links, link_type_map, self.types), trajectories)

        interesting_distance = map(lambda links: total_length(links, link_length), interesting)
        not_interesting_distance = map(lambda links: total_length(links, link_length), not_interesting)

        interesting_bucket = Buckets(0.0,50000.0, 50)
        interesting_bucket.update(interesting_distance)

        not_interesting_bucket = Buckets(0.0,50000.0, 50)
        not_interesting_bucket.update(not_interesting_distance)
        plt.subplot(2,1,1)
        plt.hist(interesting_distance, 50, (0,50000))
        plt.subplot(2,1,2)
        plt.plot(interesting_bucket.range(), map(lambda x,y : float(x)/float(x+y), interesting_bucket.buckets, not_interesting_bucket.buckets),'-o')
        plt.title(title)
        plt.xlabel("distance (m)")
        plt.ylabel("percent on " + title)

class CumulativeDistanceTraveled:
    def __init__(self):
        self.link_length = get_link_length_map()
        self.link_type_map = get_link_type_map()

        self.types = set()
        self.trajectories = get_trajectories()

    def set_types(self,types):
        self.types = set(types)

    def plot_hist(self, title):
        link_type_map = self.link_type_map
        link_length = self.link_length

        trajectories = self.trajectories
        interesting = filter(lambda links: has_types(links, link_type_map, self.types), trajectories)

        interesting_distance = map(lambda links: total_length(links, link_length), interesting)

        interesting_bucket = Buckets(0.0,100000.0, 50)
        interesting_bucket.update(interesting_distance)
        cumulative = [0]
        for index, count in enumerate(interesting_bucket.buckets):
            cumulative.append(count/1000000.0+cumulative[-1])
        cumulative.pop(0)
        plt.plot(interesting_bucket.range(), cumulative,'-o')
        plt.plot([0,100000], [.95,.95])
        plt.plot([0,100000], [.99,.99])
        plt.title(title)
        plt.xlabel("distance (m)")
        plt.ylabel("percent on " + title)
th = CumulativeDistanceTraveled()

th.set_types([u'"motorway"', u'"motorway_link"', u'"primary"', u'"primary_link"', u'"trunk"', u'"trunk_link"', u'"secondary"', u'"tertiary"'])
th.plot_hist('Motorway-Secondary')
plt.savefig('plots/Motorway-Tertiary.svg')
plt.savefig('plots/Motorway-Tertiary.png')

plt.close('all')

th.set_types([u'"motorway"', u'"motorway_link"', u'"primary"', u'"primary_link"', u'"trunk"', u'"trunk_link"', u'"secondary"'])
th.plot_hist('Motorway-Secondary')
plt.savefig('plots/Motorway-Secondary.svg')

plt.savefig('plots/Motorway-Secondary.png')

plt.close('all')

th.set_types([u'"motorway"', u'"motorway_link"', u'"primary"', u'"primary_link"'])
th.plot_hist('Motorway-Secondary')
plt.savefig('plots/Motorway-Primary.svg')
plt.savefig('plots/Motorway-Primary.png')
plt.close('all')

th.set_types([u'"motorway"', u'"motorway_link"']) #, u'"primary"', u'"primary_link"', u'"trunk"', u'"trunk_link"'])
th.plot_hist('Motorway-Motorway link')
plt.savefig('plots/Motorway-Motorway link.svg')
plt.savefig('plots/Motorway-Motorway link.png')
plt.close('all')