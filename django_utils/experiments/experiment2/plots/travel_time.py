__author__ = 'lei'
from django.db import connection
from django_utils import config
from django_utils.experiments.experiment2.database_setup.trajectory import Trajectory
import numpy as np
import matplotlib.pyplot as plt
from route_stats import RouteCreator
from django.contrib.gis.geos import LineString, GEOSGeometry


# def import_link_geometry_table():
#     cursor = connection.cursor()
#     cursor.execute('''
#     SELECT link_id, geom, geom_dist, geom_orig FROM link_geometry;
#     ''')
#     link_geom = {id: GEOSGeometry(geom_orig) for id, geom, geom_dist, geom_orig in cursor}
#     length_cache = {id:link_geom[id].length for id in link_geom.keys()}
#     return link_geom, length_cache
#
# sql_query = '''
# select links, travel_time from travel_stats;
# '''
# cursor = connection.cursor()
# cursor.execute(sql_query)
# link_geom, length_cache = import_link_geometry_table()
# trajectories = [Trajectory(l,None,link_geom,length_cache,tt) for l, tt in cursor]
#
# rc = RouteCreator(.8)
# rc.trajectories = trajectories
# print 'start routes'
# routes = rc.extract_all_routes(1)
# print [i.average for i in routes]

sql_query = '''
select
stddev_samp(s.time) as std,
avg(s.time) as mean,
count(s.*) as count,
s.link as link
from (
select abs(sum(-time)) as time, link
from events
group by person, link) s
where s.time < 10000
group by s.link;
'''
cursor = connection.cursor()
cursor.execute(sql_query)
distance=[]
travel_time = []
for std, avg, count in cursor:
    distance.append(std)
    travel_time.append(avg)
plt.plot(distance, travel_time, '.')
plt.show()