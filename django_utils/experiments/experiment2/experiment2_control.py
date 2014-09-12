import numpy as np
import scipy.io as sio
import scipy.sparse as sps

from django.db import connection

from django_utils.phidb.db.backends.postgresql_psycopg2.base import *
import django_utils.config as c
import generate_phi as gp

import pickle
import django_utils.config as config

import os
class Experiment2_Control:
    def __init__(self, output_file, phi, num_routes):
        self.output_file = output_file
        self.phi = phi

def x_generation_sql():
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
        ORDER BY r.orig_taz, r.dest_taz, r.od_route_index, r.flow_count
        """
        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD})
        return np.squeeze(np.array([row for row in cursor]))

def f_generation_sql():
    with server_side_cursors(connection):
        cursor = connection.cursor()

        sql_query = """
        SELECT sum(flow_count)
        FROM experiment2_routes
        WHERE od_route_index < %(num_routes)s
        GROUP BY orig_taz, dest_taz
        ORDER BY orig_taz, dest_taz
        """
        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD})
        return np.squeeze(np.array([row for row in cursor]))

def U_generation_sql():
    with server_side_cursors(connection):
        cursor = connection.cursor()

        sql_query = """
        SELECT count(od_route_index)
        FROM experiment2_routes
        WHERE od_route_index < %(num_routes)s
        GROUP BY orig_taz, dest_taz
        ORDER BY orig_taz, dest_taz
        """
        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD})
        block_sizes = np.squeeze(np.array([row for row in cursor]))
    return block_sizes_to_U(block_sizes)

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


def A_generation_sql(phi):
    with server_side_cursors(connection):
        cursor = connection.cursor()

        sql_query = """
        SELECT r.orig_taz AS orig, r.dest_taz AS dest, r.od_route_index
        FROM experiment2_routes r
        WHERE od_route_index < %(num_routes)s
        ORDER BY r.orig_taz, r.dest_taz, r.od_route_index, r.flow_count
        """

        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD})
        indices = [row for row in cursor]
    I,J,V = [],[],[]
    for i,(o,d,r) in enumerate(indices):

        route_to_links = phi[(o,d)][r]
        len1 = len(route_to_links)
        route_to_links = list(filter(lambda x: x!=None, route_to_links))
        len2 = len(route_to_links)
        if len1 != len2:
            print('filtered None values')

        size = len(route_to_links)
        I.extend(route_to_links)
        J.extend([i]*size)
        V.extend([1]*size)
    print (len(indices))
    return sps.csr_matrix((V,(I,J)),shape=(1033,len(indices)))


def export_matrices(OUTFILE, U, f, phi, x):
    print(U.shape)
    print(f.shape)
    print(x.shape)

    f = U.T.dot(f)
    size = f.shape[0]
    F = sps.dia_matrix(([f], [0]), shape=(size, size))

    sub_phi = A_generation_sql(phi)
    A = sub_phi.dot(F)

    b = A.dot(x)
    print(b.shape)
    directory = '%s/%s' % (c.DATA_DIR, c.EXPERIMENT_MATRICES_DIR)
    if not os.path.exists(directory):
        os.makedirs(directory)
    sio.savemat(directory +'/'+OUTFILE,
                {'A': A, 'U': U, 'x': x, 'b': b, 'f': f})


def generate_truncated_matrices(phi):
    U = U_generation_sql()
    f = f_generation_sql()
    x = x_generation_sql()

    assert (abs(np.sum(U.dot(x)) / U.dot(x).size - 1) < .0001)

    OUTFILE = "experiment2_waypoints_matrices_routes_{0}.mat".format(config.NUM_ROUTES_PER_OD)

    export_matrices(OUTFILE, U, f, phi, x)


def generate_matrices(generate_phi=True):
    path = '%s/%s' % ('/home/lei/traffic/datasets/Phi/experiment_matrices/', 'phi')

    if generate_phi:
        phi = gp.phi_generation_sql()

        with open(path, 'w') as fil:
            pickle.dump(phi, fil)
    else:
        phi = pickle.load(file(path))

    generate_truncated_matrices(phi)
    #generate_untruncated_matrices(phi)

if __name__ == "__main__":
    generate_matrices()
