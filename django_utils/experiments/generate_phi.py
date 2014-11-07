import uuid

import os
from lib import google_lines
import pickle
import random
from django.contrib.gis.geos import Point, LineString
import json
import time
import logging
import numpy as np
from lib.console_progress import ConsoleProgress

from django.db import transaction
from phidb.db.backends.postgresql_psycopg2.base import *
from collections import defaultdict

from django.db import connection
import config as c

logging.basicConfig(level=logging.DEBUG)
N_TAZ = 321
N_TAZ_TARGET = 321
N_ROUTES = 280691
FUZZY_DIST = 10

def phi_generation_sql(experiment_id):
    origins = defaultdict(dict)
    with server_side_cursors(connection):
        cursor = connection.cursor()

        gen_tt = ConsoleProgress(N_ROUTES, message="Computing Phi")
        sql_query = """
        SELECT om.matrix_id, dm.matrix_id, r.od_route_index,
        array(
          SELECT (SELECT vector_index FROM orm_experimentsensor es WHERE es.sensor_id = s.id AND es.experiment_id = %s LIMIT 1)
          FROM orm_sensor s
          WHERE ST_Distance(r.geom_dist, s.location_dist) < 10
        ) AS sensors
        FROM orm_route r, orm_matrixtaz om, orm_matrixtaz dm
        WHERE r.origin_taz = om.taz_id AND r.destination_taz = dm.taz_id
        """
        cursor.execute(sql_query, (experiment_id,))
        for row in cursor:
            gen_tt.increment_progress()
            o, d, rt, rs = row
            origins[(o, d)][rt] = rs
        gen_tt.finish()

    return origins

def generate_and_pickle_phi():
    selected_origin_id = str(time.time())
    metadata = {
      'id': selected_origin_id,
      'N_TAZ': N_TAZ,
      'N_TAZ_CONDENSED': N_TAZ,
      'FUZZY_DIST': FUZZY_DIST
    }
    pickle.dump({'phi':phi_generation_sql(), 'metadata':metadata},
            open('%s/phi_condensed%s_db.pickle' % (c.DATA_DIR,
                selected_origin_id), 'w'))
