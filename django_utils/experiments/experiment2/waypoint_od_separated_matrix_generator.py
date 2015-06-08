import numpy as np
import scipy.io as sio
import scipy.sparse as sps

from django.db import connection

from django_utils.phidb.db.backends.postgresql_psycopg2.base import *

from collections import defaultdict

import waypoint_matrix_generator as wm
from experimentmatrices import ExperimentMatrices
# groups by waypoints only
class WaypointMatrixGenerator:
    def __init__(self, phi, num_routes, waypoint_density):
        self.num_routes = num_routes
        self.waypoint_density = waypoint_density
        self.parameter_dictionary = {'num_routes':self.num_routes, 'density':self.waypoint_density}
        self.phi = phi
        self.matrices = None
        self.wm_generator = wm.WaypointMatrixGenerator
        self.x = None
        self.route_index = None

    def x_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT r.flow_count/cast(t.total as float), r.orig_taz, r.dest_taz, r.od_route_index
            FROM
            (
                select r.flow_count as flow_count,
                    r.orig_taz as orig_taz,
                    r.dest_taz as dest_taz,
                    r.od_route_index as od_route_index,
                    w.waypoints as waypoints
                from experiment2_routes r
                join experiment2_waypoint_od_bins w
                on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
                WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
                ORDER BY r.orig_taz, r.dest_taz, w.waypoints, r.od_route_index
            ) r,
            (
                SELECT sum(r.flow_count) as total, w.waypoints as waypoints
                FROM experiment2_routes r
                JOIN experiment2_waypoint_od_bins w
                on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
                WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
                GROUP BY w.waypoints
                ORDER BY w.waypoints
            ) t
            WHERE r.waypoints = t.waypoints
            ORDER BY t.waypoints, r.orig_taz, r.dest_taz, r.od_route_index;
            """
            cursor.execute(sql_query, self.parameter_dictionary)
            x = []
            index =[]
            for xi, o, d, ri in cursor:
                x.append(xi)
                index.append((o,d,ri))
            return np.squeeze(np.array(x)), index

    def f_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT sum(r.flow_count)
            from experiment2_routes r
            join experiment2_waypoint_od_bins w
            on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
            where r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
            GROUP BY w.waypoints
            ORDER BY w.waypoints
            """
            cursor.execute(sql_query, self.parameter_dictionary)
            return np.squeeze(np.array([row for row in cursor]))

    def U_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT count(r.od_route_index)
            from experiment2_routes r
            join experiment2_waypoint_od_bins w
            on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
            WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
            GROUP BY w.waypoints
            ORDER BY w.waypoints
            """
            cursor.execute(sql_query, self.parameter_dictionary)
            block_sizes = np.squeeze(np.array([row for row in cursor]))
        return WaypointMatrixGenerator.block_sizes_to_U(block_sizes)

    @staticmethod
    def block_sizes_to_U(block_sizes):
        print(block_sizes)
        total = np.sum(block_sizes)
        blocks = []
        for i in block_sizes:
            blocks.append(1)
            if i > 1:
                for j in range(i-1):
                    blocks.append(0)
        I = np.cumsum(blocks)-1

        J = np.array(range(total))
        V = np.ones(total)
        return sps.csr_matrix((V,(I,J)))

    def A_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT r.orig_taz AS orig, r.dest_taz AS dest, r.od_route_index
            from experiment2_routes r
            join experiment2_waypoint_od_bins w
            on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
            WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
            ORDER BY w.waypoints, r.orig_taz, r.dest_taz, r.od_route_index
            """
            cursor.execute(sql_query,self.parameter_dictionary)
            indices = [row for row in cursor]
        I,J,V = [],[],[]
        for i,(o,d,r) in enumerate(indices):
            route_to_links = self.phi[(o,d)][r]

            len1 = len(route_to_links)
            route_to_links = list(filter(lambda x: x!=None, route_to_links))
            len2 = len(route_to_links)
            if len1 != len2:
                print('filtered none values')

            size = len(route_to_links)
            I.extend(route_to_links)
            J.extend([i]*size)
            V.extend([1]*size)

        return sps.csr_matrix((V,(I,J)),shape=(1033,len(indices)))

    def generate_matrices(self):
        U = self.U_generation_sql()
        f = self.f_generation_sql()
        x, route_table = self.x_generation_sql()
        self.x = x

        assert(np.sum(U.dot(x)) == U.shape[0])

        f = U.T.dot(f)
        size = f.shape[0]
        F = sps.dia_matrix(([f],[0]),shape=(size,size))

        sub_phi = self.A_generation_sql()
        A = sub_phi.dot(F)
        b = A.dot(x)

        E = self.E_generation_sql()
        D = self.D_generation_sql()

        D = D.dot(F)
        A = sps.vstack((A, D))
        b = np.hstack((b, E))
        print np.sum(np.abs(D*x-E))
        self.matrices = {'A':A, 'U':U, 'x':x, 'b':b, 'f':f}
        matrices = ExperimentMatrices(A, b, x, U, f, route_table)
        return matrices

    def save_matrices(self, filename):
        if (self.matrices == None):
            self.generate_matrices()

        sio.savemat(filename, self.matrices)


    def E_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT sum(flow_count)
            FROM experiment2_routes r
            join experiment2_waypoint_od_bins w
            on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
            WHERE r.od_route_index < %(num_routes)s
            GROUP BY orig_taz, dest_taz
            ORDER BY orig_taz, dest_taz
            """
            cursor.execute(sql_query, {'num_routes':self.num_routes})
            return np.squeeze(np.array([row for row in cursor]))

    def get_od_list(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT DISTINCT r.orig_taz AS orig, r.dest_taz AS dest
            from experiment2_routes r
            WHERE r.od_route_index < %(num_routes)s
            ORDER BY r.orig_taz, r.dest_taz
            """

            cursor.execute(sql_query, self.parameter_dictionary)

            return [row for row in cursor]

        raise Exception()

    def get_od_index_map(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT r.orig_taz AS orig, r.dest_taz AS dest, r.od_route_index
            from experiment2_routes r
            join experiment2_waypoint_od_bins w
            on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
            WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
            ORDER BY w.waypoints, r.orig_taz, r.dest_taz, r.od_route_index
            """

            cursor.execute(sql_query, self.parameter_dictionary)

            od_index_map = defaultdict(list)
            for index, (o, d, i) in enumerate(cursor):
                od_index_map[(o,d)].append(index)

            return od_index_map

        raise Exception()

    def D_generation_sql(self):
        od_index_map = self.get_od_index_map()
        od_list = self.get_od_list()
        x = self.x

        D = sps.dok_matrix((len(od_list), len(x)))

        for index, (o,d) in enumerate(od_list):
            D[index, od_index_map[(o,d)]] = 1

        return sps.csr_matrix(D)
