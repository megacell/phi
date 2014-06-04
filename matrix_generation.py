'''
Created on Jun 3, 2014

@author: jeromethai
'''

"""
Generate A, U matrices
"""

N_SENSORS = 5
N_ROUTES = 4

from collections import defaultdict
from scipy.sparse import csr_matrix, lil_matrix

def matrix_generation(data, route_flows):
    wp2routes = defaultdict(list)
    wp_flows = defaultdict(float)
    route2sensors = {}
    
    for route_id, o, wp_ids, d, sensor_ids in data:
        wp2routes[(o,d,tuple(wp_ids))].append(route_id)
        wp_flows[(o,d,tuple(wp_ids))] += route_flows[route_id]
        route2sensors[route_id] = sensor_ids
    
    A = lil_matrix((N_SENSORS, N_ROUTES))
    U = lil_matrix((len(wp_flows), N_ROUTES))
    
    for route_id, o, wp_ids, d, sensor_ids in data:
        for sensor_id in route2sensors[route_id]:
            A[sensor_id, route_id] = max(0, wp_flows[(o,d,tuple(wp_ids))])
        
    row_index = 0    
    for key, route_ids in wp2routes.items():
        for route_id in route_ids:
            U[row_index, route_id] = 1 
        row_index += 1      
    
    return wp2routes, wp_flows, A, U

if __name__ == '__main__':
    data = [(0, 1, [1,2,3,4], 1, [2,3]), (1, 1, [1,2,3,4], 1, [4,0,1]), (2, 1, [1,5,3,4], 1, [1,0]), (3, 1, [5,2,1], 2, [4,0])]
    route_flows = [2, 3, 4, 5]
    data2, data3, A, U = matrix_generation(data, route_flows)
    print data2
    print data3
    print A
    print
    print U