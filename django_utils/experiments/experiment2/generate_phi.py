# import pickle

from lib.console_progress import ConsoleProgress

from django_utils.phidb.db.backends.postgresql_psycopg2.base import *
from collections import defaultdict

from django.db import connection
import django_utils.config as config

class PhiGenerator:
    def __init__(self, num_routes):
        self.num_routes = num_routes

    @staticmethod
    def route_count():
        cursor = connection.cursor()
        route_count_query = """
            SELECT COUNT(*) FROM experiment2_routes;
            """
        cursor.execute(route_count_query)
        for i in cursor:
            return i[0]
        return 0

    def phi_generation_sql(self):
        origins = defaultdict(dict)
        with server_side_cursors(connection):
            cursor = connection.cursor()
            count = PhiGenerator.route_count()

            gen_tt = ConsoleProgress(count, message="Computing Phi")
            sql_query = """
            SELECT r.orig_taz, r.dest_taz, r.od_route_index,
            array(
              SELECT (SELECT vector_index FROM orm_experimentsensor es WHERE es.sensor_id = s.id LIMIT 1)
              FROM orm_sensor s
              WHERE ST_Distance(r.geom_dist, s.location_dist) < 10 AND s.road_type ='Freeway'
            ) AS sensors
            FROM experiment2_routes r
            WHERE r.od_route_index < %(num_routes)s
            """
            cursor.execute(sql_query, {'num_routes':self.num_routes})
            for row in cursor:
                gen_tt.increment_progress()
                o, d, rt, rs = row
                origins[(o, d)][rt] = rs
            gen_tt.finish()

        return origins

def phi_generation_sql():
    pg = PhiGenerator(config.NUM_ROUTES_PER_OD)
    return pg.phi_generation_sql()
