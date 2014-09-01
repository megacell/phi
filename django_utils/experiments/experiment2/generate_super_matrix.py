__author__ = 'lei'
import numpy as np
import scipy.io as sio
import scipy.sparse as sps

from django.db import connection

from django_utils.phidb.db.backends.postgresql_psycopg2.base import *
from collections import defaultdict
import os


class GenerateSuperMatrix:
    def __init__(self, routes_per_od, waypoint_density,output_file):
        self.NUM_ROUTES_PER_OD = routes_per_od
        self.WAYPOINT_DENSITY = waypoint_density
        self.EXPERIMENT_MATRICES_DIR = output_file
        self.map_links_to_index = GenerateSuperMatrix.remap_links_to_index()

    @staticmethod
    def total_links():
        cursor = connection.cursor()
        sql_query = '''
        select count(distinct link_id) from link_geometry;
        '''
        cursor.execute(sql_query)
        return cursor.fetchone()[0]

    @staticmethod
    def remap_links_to_index():
        cursor = connection.cursor()
        sql_query = '''
        select link_index, link_id from link_geometry;
        '''
        cursor.execute(sql_query)
        return {k:v for v,k in cursor}

    def x_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT r.flow_count/cast(t.total as float)
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
                ORDER BY r.orig_taz, r.dest_taz, w.waypoints
            ) r,
            (
                SELECT sum(r.flow_count) as total, r.orig_taz as orig_taz, r.dest_taz as dest_taz, w.waypoints as waypoints
                FROM experiment2_routes r
                JOIN experiment2_waypoint_od_bins w
                on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
                WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
                GROUP BY r.orig_taz, r.dest_taz, w.waypoints
                ORDER BY r.orig_taz, r.dest_taz, w.waypoints
            ) t
            WHERE r.orig_taz = t.orig_taz AND r.dest_taz = t.dest_taz AND r.waypoints = t.waypoints
            ORDER BY r.orig_taz, r.dest_taz, t.waypoints, r.od_route_index;
            """
            cursor.execute(sql_query, {'num_routes':self.NUM_ROUTES_PER_OD, 'density':self.WAYPOINT_DENSITY})
            return np.squeeze(np.array([row for row in cursor]))

    def f_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT sum(r.flow_count)
            from experiment2_routes r
            join experiment2_waypoint_od_bins w
            on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
            where r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
            GROUP BY r.orig_taz, r.dest_taz, w.waypoints
            ORDER BY r.orig_taz, r.dest_taz, w.waypoints
            """
            cursor.execute(sql_query, {'num_routes':self.NUM_ROUTES_PER_OD, 'density':self.WAYPOINT_DENSITY})
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
            GROUP BY r.orig_taz, r.dest_taz, w.waypoints
            ORDER BY r.orig_taz, r.dest_taz, w.waypoints
            """
            cursor.execute(sql_query, {'num_routes':self.NUM_ROUTES_PER_OD, 'density':self.WAYPOINT_DENSITY})
            block_sizes = np.squeeze(np.array([row for row in cursor]))
        return GenerateSuperMatrix.block_sizes_to_U(block_sizes)

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
        print(total)
        J = np.array(range(total))
        V = np.ones(total)
        return sps.csr_matrix((V,(I,J)))

    def A_generation_sql(self):
        with server_side_cursors(connection):
            cursor = connection.cursor()

            sql_query = """
            SELECT r.orig_taz AS orig, r.dest_taz AS dest, r.od_route_index, r.links
            from experiment2_routes r
            join experiment2_waypoint_od_bins w
            on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
            WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
            ORDER BY r.orig_taz, r.dest_taz, w.waypoints, r.od_route_index
            """
            cursor.execute(sql_query, {'num_routes':self.NUM_ROUTES_PER_OD, 'density':self.WAYPOINT_DENSITY})
            indices = [row for row in cursor]
        I,J,V = [],[],[]
        for i,(o,d,r, links) in enumerate(indices):
            route_to_links = [self.map_links_to_index[link] for link in links]

            assert(len(filter(lambda x: x==None, route_to_links)) == 0)

            size = len(route_to_links)
            I.extend(route_to_links)
            J.extend([i]*size)
            V.extend([1]*size)
        print (len(indices))
        return sps.csr_matrix((V,(I,J)),shape=(GenerateSuperMatrix.total_links(),len(indices)))

    @staticmethod
    def set_diff(A,B):
        return np.array(list(set(A).difference(set(B))))

    def generate_matrices(self):
        U = self.U_generation_sql()
        f = self.f_generation_sql()
        x = self.x_generation_sql()


        assert(np.sum(U.dot(x)) == U.shape[0])

        print(U.shape)
        print(f.shape)
        print(x.shape)

        f = U.T.dot(f)
        size = f.shape[0]
        F = sps.dia_matrix(([f],[0]),shape=(size,size))

        sub_phi = self.A_generation_sql()
        A = sub_phi.dot(F)
        b = A.dot(x)
        #control_matrices = sio.loadmat(open(c.DATA_DIR + '/experiment_matrices/experiment2_control_matrices_routes_2000.mat'))
        #b = control_matrices['b']
        print(A.shape)
        print(b.shape)
        print(np.sum(b))
        OUTFILE = "experiment2_total_link_matrices_routes_{0}.mat".format(self.NUM_ROUTES_PER_OD)
        directory = self.EXPERIMENT_MATRICES_DIR
        if not os.path.exists(directory):
            os.makedirs(directory)
        sio.savemat('%s/%s' % (directory, OUTFILE),
                {'A':A, 'U':U, 'x':x, 'b':b, 'f':f})