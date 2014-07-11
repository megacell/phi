from django.db import connection
from phidb.db.backends.postgresql_psycopg2.base import *

import pickle
import config as c

def waypoint_bins():
    with server_side_cursors(connection):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM waypoint_od_bins LIMIT 10")
        for row in cursor:
            print row
    return None

def cross_validation_ids():
    with server_side_cursors(connection):
        cursor = connection.cursor()
        cursor.execute("SELECT id,taz_id FROM orm_sensor")
        results = [row for row in cursor]
        with open('%s/%s/taz_ids.pkl' % (c.DATA_DIR,c.ESTIMATION_INFO_DIR),'w') as f:
            pickle.dump(results,f)

        cursor = connection.cursor()
        cursor.execute("SELECT id,city_id FROM orm_sensor")
        results = [row for row in cursor]
        with open('%s/%s/city_ids.pkl' % (c.DATA_DIR,
            c.ESTIMATION_INFO_DIR),'w') as f:
            pickle.dump(results,f)

        cursor = connection.cursor()
        cursor.execute("SELECT id,name FROM orm_sensor")
        results = [row for row in cursor]
        with open('%s/%s/street_names.pkl' % (c.DATA_DIR,
            c.ESTIMATION_INFO_DIR),'w') as f:
            pickle.dump(results,f)
    return None

def route_weights():
    with server_side_cursors(connection):
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT vector_index,travel_time FROM " + \
            "orm_experimentroute, orm_route WHERE " + \
            "orm_experimentroute.route_id = orm_route.id ORDER BY vector_index")
        results = [row for row in cursor]
        with open('%s/%s/travel_times.pkl' % (c.DATA_DIR,
            c.ESTIMATION_INFO_DIR),'w') as f:
            pickle.dump(results,f)
    return None

