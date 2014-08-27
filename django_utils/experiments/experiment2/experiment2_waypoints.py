import numpy as np
import scipy.io as sio
import scipy.sparse as sps

from django.db import connection

from django_utils.phidb.db.backends.postgresql_psycopg2.base import *
import django_utils.config as c
import django_utils.config as config
import generate_phi as gp

import pickle
import os
OUTFILE = "experiment2_waypoint_matrices.mat"

def x_generation_sql():
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
        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD, 'density':config.WAYPOINT_DENSITY})
        return np.squeeze(np.array([row for row in cursor]))

def f_generation_sql():
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
        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD, 'density':config.WAYPOINT_DENSITY})
        return np.squeeze(np.array([row for row in cursor]))


def U_generation_sql():
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
        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD, 'density':config.WAYPOINT_DENSITY})
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
    print(total)
    J = np.array(range(total))
    V = np.ones(total)
    return sps.csr_matrix((V,(I,J)))


def A_generation_sql(phi):
    with server_side_cursors(connection):
        cursor = connection.cursor()

        sql_query = """
        SELECT r.orig_taz AS orig, r.dest_taz AS dest, r.od_route_index
        from experiment2_routes r
        join experiment2_waypoint_od_bins w
        on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
        WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
        ORDER BY r.orig_taz, r.dest_taz, w.waypoints, r.od_route_index
        """
        cursor.execute(sql_query, {'num_routes':config.NUM_ROUTES_PER_OD, 'density':config.WAYPOINT_DENSITY})
        indices = [row for row in cursor]
    I,J,V = [],[],[]
    for i,(o,d,r) in enumerate(indices):
        route_to_links = phi[(o,d)][r]

        len1 = len(route_to_links)
        route_to_links = list(filter(lambda x: x!=None, route_to_links))
        len2 = len(route_to_links)
        if len1 != len2:
            pass
            #print('filtered none values')

        size = len(route_to_links)
        I.extend(route_to_links)
        J.extend([i]*size)
        V.extend([1]*size)
    print (len(indices))
    return sps.csr_matrix((V,(I,J)),shape=(1033,len(indices)))

def set_diff(A,B):
    return np.array(list(set(A).difference(set(B))))

def generate_matrices(generate_phi=True):
    path = '%s/%s' % ('/home/lei/traffic/datasets/Phi/experiment_matrices/', 'phi')

    if generate_phi:
        phi = gp.phi_generation_sql()

        with open(path, 'w') as fil:
            pickle.dump(phi, fil)
    else:
        phi = pickle.load(file(path))

    U = U_generation_sql()
    f = f_generation_sql()
    x = x_generation_sql()


    # for i in range(3):
    #     zs = np.nonzero(f==0)[0]
    #     zs_routes = np.searchsorted(U.nonzero()[0],zs)
    #     nz_routes = set_diff(range(x.shape[0]),zs_routes)
    #
    #     U = U[:,nz_routes]
    #     nz = np.array(list(set(U.nonzero()[0])))
    #     f = f[nz]
    #     x = x[nz_routes]
    #     U = U[nz,:]

    assert(np.sum(U.dot(x)) == U.shape[0])

    print(U.shape)
    print(f.shape)
    print(x.shape)

    f = U.T.dot(f)
    size = f.shape[0]
    F = sps.dia_matrix(([f],[0]),shape=(size,size))

    sub_phi = A_generation_sql(phi)
    A = sub_phi.dot(F)
    b = A.dot(x)
    print(b.shape)
    OUTFILE = "experiment2_waypoints_matrices_routes_{0}.mat".format(config.NUM_ROUTES_PER_OD)
    directory = '%s/%s' % (c.DATA_DIR,c.EXPERIMENT_MATRICES_DIR)
    if not os.path.exists(directory):
        os.makedirs(directory)
    sio.savemat('%s/%s' % (directory, OUTFILE),
            {'A':A, 'U':U, 'x':x, 'b':b, 'f':f})

if __name__ == "__main__":
    generate_matrices()
