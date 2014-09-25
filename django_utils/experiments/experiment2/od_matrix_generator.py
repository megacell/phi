import numpy as np
import scipy.io as sio
import scipy.sparse as sps

from django.db import connection

from django_utils.phidb.db.backends.postgresql_psycopg2.base import *

class ODMatrixGenerator:
    def __init__(self, phi, num_routes):
        self.phi = phi
        self.num_routes = num_routes
        self.matrices = None

    def x_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT r.flow_count/cast(t.total as float)
            FROM experiment2_routes r,
            (
                SELECT sum(flow_count) as total, orig_taz as orig_taz, dest_taz as dest_taz
                FROM experiment2_routes
                WHERE od_route_index < %(num_routes)s
                GROUP BY orig_taz, dest_taz
                ORDER BY orig_taz, dest_taz
            ) t
            WHERE r.orig_taz = t.orig_taz AND r.dest_taz = t.dest_taz AND r.od_route_index < %(num_routes)s
            ORDER BY r.orig_taz, r.dest_taz, r.od_route_index
            """
            cursor.execute(sql_query, {'num_routes':self.num_routes})
            return np.squeeze(np.array([row for row in cursor]))

    def f_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT sum(flow_count)
            FROM experiment2_routes
            WHERE od_route_index < %(num_routes)s
            GROUP BY orig_taz, dest_taz
            ORDER BY orig_taz, dest_taz
            """
            cursor.execute(sql_query, {'num_routes':self.num_routes})
            return np.squeeze(np.array([row for row in cursor]))

    def U_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT count(od_route_index)
            FROM experiment2_routes
            WHERE od_route_index < %(num_routes)s
            GROUP BY orig_taz, dest_taz
            ORDER BY orig_taz, dest_taz
            """
            cursor.execute(sql_query, {'num_routes':self.num_routes})
            block_sizes = np.squeeze(np.array([row for row in cursor]))
        return ODMatrixGenerator.block_sizes_to_U(block_sizes)

    @staticmethod
    def block_sizes_to_U(block_sizes):
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
            FROM experiment2_routes r
            WHERE od_route_index < %(num_routes)s
            ORDER BY r.orig_taz, r.dest_taz, r.od_route_index, r.flow_count
            """

            cursor.execute(sql_query, {'num_routes':self.num_routes})
            indices = [row for row in cursor]
        I,J,V = [],[],[]
        for i,(o,d,r) in enumerate(indices):

            route_to_links = self.phi[(o,d)][r]
            len1 = len(route_to_links)
            route_to_links = list(filter(lambda x: x!=None, route_to_links))
            len2 = len(route_to_links)
            if len1 != len2:
                print('filtered None values')

            size = len(route_to_links)
            I.extend(route_to_links)
            J.extend([i]*size)
            V.extend([1]*size)
        return sps.csr_matrix((V,(I,J)),shape=(1033,len(indices)))


    def generate_matrices(self):
        U = self.U_generation_sql()
        f = self.f_generation_sql()
        x = self.x_generation_sql()

        assert(np.sum(U.dot(x)) == U.shape[0])

        f = U.T.dot(f)
        size = f.shape[0]
        F = sps.dia_matrix(([f],[0]),shape=(size,size))

        sub_phi = self.A_generation_sql()
        A = sub_phi.dot(F)
        b = A.dot(x)

        self.matrices = {'A':A, 'U':U, 'x':x, 'b':b, 'f':f}

        return self.matrices

    def save_matrices(self, filename):
        if (self.matrices == None):
            self.generate_matrices()
        sio.savemat(filename, self.matrices)