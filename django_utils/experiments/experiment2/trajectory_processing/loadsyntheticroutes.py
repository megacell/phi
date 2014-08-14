import csv
from multiprocessing import Pool

import django_utils.config as config
from trajectory import Trajectory
from django_utils.experiments.experiment2.trajectory_processing.geometry_map import GeometryMap
from group_trajectories import group_by_od
from route import Route
import pickle
from lib.console_progress import ConsoleProgress


canonical_projection = 4326
google_projection = 3857  # 900913 # alternatively 3857

class syntheticdataloader:
    def __init__(self):
        pass

    def create_trajectory(self, index, trajectory_row):
        trajectory = [int(x) for x in trajectory_row['route_string'].strip().split(' ')]

        od_taz = (float(trajectory_row['orig_TAZ']), float(trajectory_row['dest_TAZ']))
        return Trajectory(trajectory, od_taz, GeometryMap.map_origID_to_geometry())

    def load_trajectories(self):
        trajectories = list()
        with open(config.DATA_DIR + '/OD_500k.csv') as odcsv:
            trajectory_table = csv.DictReader(odcsv)
            for index, trajectory_row in enumerate(trajectory_table):
                trajectory = self.create_trajectory(index, trajectory_row)
                trajectories.append(trajectory)
                #if (index > 1000): break
        return trajectories

def create_routes_from_od_group(group):
    matches = group[1].get_matches(3)
    assert (len(matches) <= 50)
    od_taz = group[0]
    routes = list()
    for match in matches:
        routes.append(Route(od_taz, match[0], len(match[1])))
    return routes

def compareRoutes(r1,r2):
    return -r1._agent_count + r2._agent_count

def flatten(l):
    return [j for i in l for j in i]


def load():
    loader = syntheticdataloader()
    trajectories = loader.load_trajectories()
    od_groups = group_by_od(trajectories)
    #pool = Pool()
    print('begin od to route')
    print len(od_groups.keys())

    od = [len(od_groups[k]._trajectories) for k in od_groups.keys()]
    od.sort()
    od.reverse()
    print od[:10]
    cp = ConsoleProgress(len(od_groups.keys()))
    def f(g):
        cp.increment_progress()
        routes = create_routes_from_od_group(g)
        return routes
    routes = map(f , ((k, od_groups[k]) for k in od_groups.keys()))
    routes = flatten(routes)

    print(len(routes))

    routes.sort(compareRoutes)
    print 'begin pickling'
    output = open('data.pkl', 'wb')
# Pickle dictionary using protocol 0.
    pickle.dump(routes, output)
    print routes[:5]
