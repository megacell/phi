import scipy.io as sio
import numpy as np
import scipy.sparse as sps
from django.db import connection
from cStringIO import StringIO
def flatten(xs):
    return np.array(xs).flatten()
def writetodb(route_table, x_true, x_est, flow):
    cursor = connection.cursor()
    x_true = flatten(x_true)
    x_est = flatten(x_est)
    flow = flatten(flow)

    sql_query = '''
    DROP TABLE IF EXISTS visualization_routes;
    CREATE TABLE visualization_routes
    (
    o int,
    d int,
    od_route_index int,
    x_true float,
    x_est float,
    flow float
    )
    '''

    cursor.execute(sql_query)

    stringIO = StringIO()
    for (o,d, index), x_t, x_e, f in zip(route_table, x_true, x_est, flow):
        stringIO.write('\t'.join(map(str, [o, d, index, x_t, x_e, f])))
        stringIO.write('\n')
    stringIO.reset()
    cursor.copy_from(stringIO, 'visualization_routes')

def block_sizes_from_U(U):
    # Sum along rows
    return np.asarray(map(int, np.squeeze(np.asarray(U.sum(axis=1)))))

def block_sizes_to_N(block_sizes):
    """Converts a list of the block sizes to a scipy.sparse matrix.

    The matrix will start in lil format, as this is the best way to generate it,
    but can easily be converted to another format such as csr for efficient multiplication.
    I will return it in csr so that each function doesn't need to convert it itself.
    """
    block_sizes = np.squeeze(np.asarray(block_sizes))
    m = int(np.sum(block_sizes))
    n = int(m - block_sizes.shape[0])
    N = sps.lil_matrix((m, n))
    start_row = 0
    start_col = 0
    for i, block_size in enumerate(block_sizes):
        if block_size < 2:
            start_row += block_size
            start_col += block_size - 1
            continue
        for j in xrange(block_size-1):
            N[start_row+j, start_col+j] = 1
            N[start_row+j+1, start_col+j] = -1
        start_row += block_size
        start_col += block_size - 1
    return N.tocsr()

def block_sizes_to_x0(block_sizes):
    """Converts a list of the block sizes to a scipy.sparse vector x0
    """
    x0 = sps.dok_matrix((np.sum(block_sizes),1))
    for i in np.cumsum(block_sizes)-1: x0[(i,0)] = 1
    return x0.transpose()

path = '/home/lei/traffic/datasets/Phi/experiment_matrices/950'

problem_file = sio.loadmat(path + '/experiment2_waypoints_matrices_routes_50.mat')
solution_file = sio.loadmat(path + '/output_waypoints50.mat')

print problem_file
print solution_file

A = problem_file['A']
U = problem_file['U']
x_true = problem_file['x']
f = problem_file['f']

z_est = solution_file['x']
block_sizes = block_sizes_from_U(U)
N = block_sizes_to_N(block_sizes)
x0 = block_sizes_to_x0(block_sizes)
x_est = x0.T + N*z_est.T

writetodb(problem_file['route_table'], x_true, x_est, f)