import numpy as np
import scipy.io as sio
import scipy.sparse as sps

import psycopg2
import config
import pickle
import csv

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
        from experiment2_routes r
        join experiment2_waypoint_od_bins w
        on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
        WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
        GROUP BY w.waypoints
        ORDER BY w.waypoints
        """
        cur = self.query(sql)
        block_sizes = np.squeeze(np.array([row for row in cur]))
        return block_sizes_to_U(block_sizes)
        
    def f(self):
        sql = """
        SELECT w.waypoints
        from experiment2_routes r
        join experiment2_waypoint_od_bins w
        on r.od_route_index = w.od_route_index and r.orig_taz = w.origin and r.dest_taz = w.destination
        WHERE r.od_route_index < %(num_routes)s AND w.density_id = %(density)s
        GROUP BY w.waypoints
        ORDER BY w.waypoints
        """
        OFFSET = 72341
        reader = csv.DictReader(open(config.SSTEM_DATA))
        cellpath_flows = defaultdict(int)
        print 'Loading SSTEM...'
        
        for row in reader:
            if row['commute_direction'] == '0':
                cellpath = tuple(sorted(set(map(int, row['cells_ID_string'].split()))))
                cellpath_flows[cellpath] += 1

        print 'Total agents in SSTEM: {}'.format(sum(cellpath_flows.values()))
        
        cur = self.query(sql)
        f = []
        for row in cur:
            a = tuple(sorted(set(map(lambda x: x - OFFSET, row[0]))))
            f.append(cellpath_flows[a])
        print 'Agents used in SSTEM: {}'.format(sum(f))
        return np.array(f)

    def save_matrices(self):
        print 'Generating A'
        A = self.A()
        print 'Generating b'
        b = self.b()
        print 'Generating U'
        U = self.U()
        print 'Generating f'
        f = self.f()        
        matrices = {'A': A, 'b': b, 'U': U, 'f': f}
        print 'Saving matrices'
        sio.savemat('{}/att_experiment_2_{}.mat'
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
