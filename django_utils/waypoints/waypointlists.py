from django_utils.orm.models import Route, Waypoint
from django_utils.phidb.db.backends.postgresql_psycopg2.base import *
from django.db import connection
from collections import defaultdict
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import Point, LineString

canonical_projection = 4326

def read_waypoints():
    sql = '''
    SELECT orm_route_id, waypoints
    FROM waypoint_od_bins
    '''
    l = []
    with server_side_cursors(connection):
        cursor = connection.cursor()
        cursor.execute(sql)
        for i in cursor:
            l.append((i[0], tuple(i[1])))
    return l

def group_waypoints(l):
    waypoints_group = defaultdict(list)
    for v, k in l:
        waypoints_group[k].append(v)
    return waypoints_group

def get_all_waypoint_geometries():
    waypoints = Waypoint.objects.all()
    waypoint_geometries = {row.id: row.geom for row in waypoints}
    return waypoint_geometries

def get_waypoint_geometries(waypoint_set):
    all_waypoint_geometries = get_all_waypoint_geometries()
    return {k:all_waypoint_geometries[k] for k in waypoint_set}

def get_geometries_intersecting_segment(o, d, geometries):
    return [1]
    #sort this so that everything closest to o is first

def get_route_line(routeid):
    row = Route.objects.get(id=routeid)
    return row.geom

def generate_waypoint_sequence(lines, geometries):
    segments = list()
    for i in range(len(lines) - 1):
        list.append(get_geometries_intersecting_segment(lines[i], lines[i+1], geometries))
    return segments

def convert_waypoint_sets_to_sequences():
    # get all waypoint sets from table
    waypoints = read_waypoints()

    # find all the nonunique waypoint sets
    waypoint_groups = group_waypoints(waypoints)
    nonunique_waypoint_groups = {k:v for k, v in waypoint_groups if len(v)>1}

    # for each nonunique waypoint set
        # read the geometry of the route
        # find intersecting geometries
    for waypointset, routeids in nonunique_waypoint_groups:
        # get the geometry objects associated with the waypointset
        waypoint_geometries = get_waypoint_geometries(waypointset)
        for routeid in routeids:
            route_line = get_route_line(routeid)
            # get a sequence of waypoints that intersect the lines
            sequence = generate_waypoint_sequence(route_line, waypoint_geometries)
            # TODO: clean up sequence
            # TODO: write sequence to db



# print group_waypoints(read_waypoints()[:10])
print (get_waypoint_geometries())
print (len(get_waypoint_geometries()))
