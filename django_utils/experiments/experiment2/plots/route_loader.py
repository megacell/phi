import csv
import django_utils.config as config
from django.contrib.gis.geos import LineString, GEOSGeometry
from django.db import connection
from django_utils.experiments.experiment2.database_setup.trajectory import Trajectory
from route_stats import RouteCreator
from multiprocessing import Pool
from itertools import chain
import cStringIO
from django_utils.experiments.experiment2.database_setup.route import Route
import timeit

class RouteLoader:
    def __init__(self, routecreator_factory, connection):
        self.routecreator_factory = routecreator_factory
        self.connection = connection
        self.link_geom = dict()
        self.length_cache = dict()
        self.commute_direction = 0

    def import_link_geometry_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        SELECT link_id, geom, geom_dist, geom_orig FROM link_geometry;
        ''')
        self.link_geom = {id: GEOSGeometry(geom_orig) for id, geom, geom_dist, geom_orig in cursor}
        self.length_cache = {id: self.link_geom[id].length for id in self.link_geom.keys()}

    def get_ods(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        SELECT orig_TAZ, dest_TAZ
        FROM experiment2_trajectories
        WHERE commute_direction = %s
        GROUP BY orig_TAZ, dest_TAZ;
        ''', (self.commute_direction,))
        return [(o,d) for o, d in cursor]

    def get_trajectories(self, o,d):
        cursor = self.connection.cursor()
        cursor.execute('''
        SELECT link_ids, travel_time(link_ids)
        FROM experiment2_trajectories
        WHERE orig_TAZ = %s AND dest_TAZ = %s
        AND commute_direction = %s;
        ''', (o, d, self.commute_direction))

        trajectories = list()
        for link_ids, travel_time in cursor:
            t = Trajectory(link_ids, (o,d), self.link_geom, self.length_cache, travel_time)
            trajectories.append(t)

        return trajectories

    def import_trajectory_groups(self):
        ods = self.get_ods()
        return [self.get_trajectories(o,d) for o,d in ods]

    @staticmethod
    def create_route_list(od_index, route):
        o, d = route.od_taz_id

        return '\t'.join([str(int(o)), str(int(d)), str(od_index), str(route._agent_count), str(route.average), str(route.var)])

    def extract_routes_from_group(self, group):
        routecreator = self.routecreator_factory()
        routecreator.set_trajectories(group)

        extractedroutes = routecreator.extract_all_routes()

        return [RouteLoader.create_route_list(number, row) for number, row in enumerate(extractedroutes)]

    def group_routes(self, groups):
        tic = timeit.default_timer()
        routes = map(f, groups)
        toc = timeit.default_timer()
        print toc - tic
        rows = '\n'.join(chain.from_iterable(routes))

        sio = cStringIO.StringIO(rows)
        cursor = connection.cursor()
        cursor.copy_from(sio, 'experiment2_route_stats')
        return routes

    def load_routes(self):
        tic = timeit.default_timer()
        groups = self.import_trajectory_groups()
        toc = timeit.default_timer()
        print toc - tic


        cursor = connection.cursor()
        cursor.execute('''
        DROP TABLE IF EXISTS experiment2_route_stats CASCADE;
        CREATE TABLE experiment2_route_stats (
        orig_TAZ int,
        dest_TAZ int,
        od_route_index int,
        flow_count int,
        mean float,
        var float);
        ''')

        for g in slice(groups, 1000):
            routes = self.group_routes(g)
        print (len(routes))
def slice(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def f(g):
    routecreator = RouteCreator(config.SIMILARITY_FACTOR)
    routecreator.set_trajectories(g)

    extractedroutes = routecreator.extract_all_routes()

    return [RouteLoader.create_route_list(number, row) for number, row in enumerate(extractedroutes)]

def load():
    r = RouteLoader(lambda : RouteCreator(config.SIMILARITY_FACTOR), connection)
    r.import_link_geometry_table()
    r.load_routes()

if __name__ == '__main__':
    load()
