import numpy as np
import scipy.io as sio
import scipy.sparse as sps

import psycopg2
import config
import pickle
import json
import csv
import os

from collections import defaultdict
from pdb import set_trace as T

# Set when loading data
ATT_WAYPOINT_DENSITY = 1

class MatrixGenerator():
    def __init__(self, num_routes = 1):
        self.conn = psycopg2.connect(database='geodjango', user='megacell')
        self.params = { 'num_routes': num_routes
                      , 'density'   : ATT_WAYPOINT_DENSITY}
        self.pems = pickle.load(open(config.PEMS_LINKS))

        # PEMS links numbered by sorted Link IDs in A and b
        self.pems_indexmap = {link_id: i for i, link_id in
                              enumerate(sorted(self.pems.keys()))}
                
    def query(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql, self.params)
        return cur

    def A(self):
        '''Link-route incidence matrix, only contains links on PEMS sensors.
        '''
        
        sql = '''
        SELECT r.links
        FROM experiment2_routes r
        JOIN experiment2_waypoint_od_bins w
        ON r.od_route_index = w.od_route_index AND
           r.orig_taz = w.origin AND
           r.dest_taz = w.destination
        WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
        ORDER BY w.waypoints, r.orig_taz, r.dest_taz, r.od_route_index;
        '''
        sensed_ids = set(self.pems.keys())
        
        i = 0
        I,J,V = [],[],[]
        for row in self.query(sql):
            links = row[0]
            sensed_links = [self.pems_indexmap[l] for l in links if l in sensed_ids]
            I.extend(sensed_links)
            J.extend([i] * len(sensed_links))
            V.extend([1] * len(sensed_links))
            i += 1
        return sps.csr_matrix((V,(I,J)),shape=(len(sensed_ids),i))
            
    def b(self, start=7, end=10):
        ''' Link counts between start and end hours (inclusive)'''
        b = [0] * len(self.pems)
        for linkid, i in self.pems_indexmap.items():
            b[i] = sum(self.pems[linkid][start:end+1])
        return np.array(b)
        
    def U(self):
        sql = """
        SELECT count(r.od_route_index)
        FROM experiment2_routes r
        JOIN experiment2_waypoint_od_bins w
        ON r.od_route_index = w.od_route_index AND r.orig_taz = w.origin AND r.dest_taz = w.destination
        WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
        GROUP BY w.waypoints
        ORDER BY w.waypoints
        """
        cur = self.query(sql)
        block_sizes = np.squeeze(np.array([row for row in cur]))
        return block_sizes_to_U(block_sizes)
        
    def f(self):
        sstem_paths = json.load(open('f_patched_cellpath.json'))
        f = np.zeros(len(list(self.get_cellpaths())))
        failed = 0
        for item in sstem_paths:
            if item is None:
                failed += 1
                continue
            pathid, percent_match = item
            f[pathid] += 1
        print 'Total agents: {} Failed to match {}'.format(len(sstem_paths), failed)
        return f

    def get_cellpaths(self):
        if not os.path.isfile(config.CELLPATHS_CACHE):
            self.cache_cellpaths()
        with open(config.CELLPATHS_CACHE) as cellpaths:
            for line in cellpaths:
                yield map(int, line.split())

    def cache_cellpaths(self):
        sql = """
        SELECT w.waypoints
        FROM experiment2_routes r
        JOIN experiment2_waypoint_od_bins w
        ON r.od_route_index = w.od_route_index AND r.orig_taz = w.origin AND r.dest_taz = w.destination
        WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
        GROUP BY w.waypoints
        ORDER BY w.waypoints
        """
        with open(config.CELLPATHS_CACHE, 'w') as outfile:
            for row in self.query(sql):
                print >>outfile, ' '.join(map(str, row[0]))

    def save_matrices(self):
        print 'Generating A'
        A = self.A()
        print 'Generating b'
        b = self.b()
        print 'Generating U'
        U = self.U()
        print 'Generating f'
        f = self.f()
        x_false = np.zeros(A.shape[1])
        matrices = {'A': A, 'b': b, 'U': U, 'f': f, 'x_true': x_false}
        print 'Saving matrices'
        sio.savemat('{}/188/experiment2_waypoints_matrices_routes_{}.mat'
                    .format(config.EXPERIMENT_MATRICES_DIR, self.params['num_routes']),
                    matrices)

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

if __name__ == '__main__':
    mg = MatrixGenerator(num_routes=10)
    mg.save_matrices()

