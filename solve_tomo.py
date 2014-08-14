"""
Solve network tomography problem with radiation model as a baseline
"""
import sys
import os
import argparse
import logging
import pickle
import numpy as np
from scipy.sparse import csr_matrix, lil_matrix
from scipy.sparse.linalg import lsqr
import scipy.io as sio
import itertools

from matplotlib import pyplot as plt

from django_utils.experiments.experiment1 import generate_phi
from lib.console_progress import ConsoleProgress
import phi_ds
import x_matrix
import radiation_model
import sensors


#### HACK
django_path = (os.path.join(os.path.dirname(os.path.abspath(__file__)), 'django_utils'))
sys.path.insert(0, django_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_geo")

#### END HACK

args = []
args_set = None
data_prefix = None
ACCEPTED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'WARN']

#############
# Constants #
#############
# Size of problem
N_TAZ = 321
N_TAZ_CONDENSED = 150
N_ROUTES = 280691
N_ROUTES_CONDENSED = 60393
N_SENSORS = 1033
FIRST_ROUTE = 0

# Test choice for data verification
TEST_ORIGIN = 123
TEST_DESTINATION = 10
TEST_ROUTE = 0

def main():
    global args_set, data_prefix
    parser = argparse.ArgumentParser(description='Solve Tomography problem with radiation model.')
    parser.add_argument('--verbose', dest='verbose',
                       const=True, default=False, action='store_const',
                       help='Show verbose output (default: silent)')
    parser.add_argument('--data-prefix', dest='prefix', nargs='?', const='data',
                       default='.', help='Set prefix for data files (default: .)')
    parser.add_argument('--log', dest='log', nargs='?', const='INFO',
                       default='WARN', help='Set log level (default: WARN)')
    parser.add_argument('--compute-route-matrix', '-x', dest='compute_x',
                       const=True, default=False, action='store_const',
                       help='Compute the routing matrix instead of loading from a file (default: False)')
    parser.add_argument('--compute-od-matrix', '-A', dest='compute_a',
                       const=True, default=False, action='store_const',
                       help='Compute the OD matrix instead of loading from a file (default: False)')
    parser.add_argument('--travel-times', '-tt', dest='travel_times',
                       const=True, default=False, action='store_const',
                       help='Use travel times to compute routing matrix. Only runs if --compute-route-matrix is set. (default: False)')
    parser.add_argument('--verify-routes', dest='verify_routes',
                       const=True, default=False, action='store_const',
                       help='Use real sensors for tomography. (default: False)')
    parser.add_argument('--real-sensors', '-s', dest='real_sensors',
                       const=True, default=False, action='store_const',
                       help='Use real sensors for tomography. (default: False)')
    args_set = parser.parse_args()

    ConsoleProgress.verbose = args_set.verbose
    if args_set.verbose:
        logging.basicConfig(level=logging.DEBUG)
    if args_set.log in ACCEPTED_LOG_LEVELS:
        logging.basicConfig(level=eval('logging.'+args_set.log))
    if args_set.travel_times:
        logging.info('Using travel times.')
    if args_set.travel_times and not args_set.compute_x:
        logging.warn('Computing the routing matrix using travel times does not happen if the matrix is loaded from a file')
    if args_set.real_sensors:
        logging.info('Using real sensors for tomography solution.')
    if args_set.prefix[-1] == '/':
        data_prefix = args_set.prefix[:-1]
    else:
        data_prefix = args_set.prefix
    phi_ds.Phi.data_prefix = data_prefix
    x_matrix.XMatrix.data_prefix = data_prefix
    radiation_model.RadiationModel.data_prefix = data_prefix
    args = args_set

if __name__ == "__main__":
    main()
    args = args_set

condensed_map = pickle.load(open(data_prefix+"/small_condensed_map.pickle"))
if len(condensed_map.keys()) != N_TAZ_CONDENSED:
    raise
full_phi = phi_ds.Phi(generate_phi=generate_phi)

x_matrix = x_matrix.XMatrix(args.compute_x, full_phi, condensed_map=condensed_map, generate_phi=generate_phi, use_travel_times=args.travel_times)

if args.verify_routes:
    sensors = full_phi.data()[(TEST_ORIGIN, TEST_DESTINATION)][TEST_ROUTE]
    print "Data loaded, sample path: %s" % str(sensors)

# Read pre-computed trip counts for all OD pairs (simulated with radiation model)
rad_model = radiation_model.RadiationModel()
radflow = rad_model.as_flow()

Use_Real_Sensors = args.real_sensors

sensor_data = sensors.Sensors(Use_Real_Sensors, x_matrix, radflow)
radflow = sensor_data.get_flow()
sensors = sensor_data.sensors
yescounts = sensor_data.yescounts

#
# wlse_tomogravity solved with sparse least squares   
#
lsqr_progress = ConsoleProgress(5, args.verbose, message='Solving LSQR')
bw = sensors - x_matrix.X*radflow
Xcsr = csr_matrix(x_matrix.X)
lsqr_progress.update_progress(1)
tw = lsqr(Xcsr[yescounts,:], bw[yescounts], damp = 100)[0]

plt.hold(True)

# transform tw back to t
t = radflow[:,0] + tw
lsqr_progress.finish()

c_lsqr = x_matrix.X*t
c_rad = x_matrix.X*radflow[:,0]

indexes = [i*N_TAZ_CONDENSED+j for (i, j) in itertools.combinations(condensed_map.keys(), 2)]
t_sampled = t[np.array(indexes)]

# plot LSQR solution vs sensors
# TODO: make this a command line flag to plot
# plt.hold(True)
# plt.plot(c_lsqr,sensors,'ro')
# plt.show()
sio.savemat(data_prefix+'/sensor_fit.mat', {'lsqr_soln':c_lsqr, 'true':sensors})

plt.hist(radflow[:,0], bins=1000, histtype='stepfilled', normed=True, color='b', label='Radiation')
plt.hist(t, bins=100, histtype='stepfilled', normed=True, color='r', alpha=0.5, label='Tomoradiation')
plt.legend()

plt.figure()
n,b = np.histogram(radflow[:,0], bins=1000)
tf = n*(b[1:]+b[0:-1])/2.
tf.astype(float)
n.astype(float)
plt.plot(1 - np.cumsum(n)/float(n.sum()), 1. - (np.cumsum(tf)/n.dot(b[1:])), label='Radiation')
n,b = np.histogram(t, bins=1000)
tf = n*(b[1:]+b[0:-1])/2.
tf.astype(float)
n.astype(float)
plt.plot(1 - np.cumsum(n)/float(n.sum()), 1. - (np.cumsum(tf)/n.dot(b[1:])), label='Tomoradiation', color='r')
sio.savemat(data_prefix+'/od_flow_hist.mat', {'flow':radflow[:,0]})
sio.savemat(data_prefix+'/od_flow_hist_soln.mat', {'flow':radflow[:,0], 'soln':1. - (np.cumsum(tf)/n.dot(b[1:]))})
plt.xlabel("Fraction of OD pairs")
plt.ylabel("Percent of total network flow captured")
plt.legend(loc=4)

plt.show()

flow_model = np.array(t.reshape((N_TAZ,N_TAZ)))

lookup = pickle.load(open(data_prefix+'/lookup.pickle'))
rlookup = {}
for index in lookup:
  rlookup[lookup[index]] = index

data = []
with open(data_prefix+'/radiation_results.csv') as fopen:
  for row in fopen:
    data.append(map(float, row.strip().split(',')[:-1]))

A = lil_matrix((N_SENSORS, N_ROUTES_CONDENSED))

if args.compute_a:
    a_gen_progress = ConsoleProgress(N_ROUTES, args.verbose, message="Generating A matrix")
    col_index = 0
    for i in range(len(data)-1):
        for j in range(len(data)-1):
            if i > 0 and j > 0 and i != j:
                origin, destination = rlookup[data[0][i]], rlookup[data[j][0]]
                if origin in condensed_map and destination in condensed_map:
                    routes = full_phi.data()[origin][destination]
                    for route_index, row_indices in enumerate(routes):
                        for row_index in row_indices:
                            A[row_index, col_index] = max(0, flow_model[origin, destination])
                        col_index = col_index + 1
                        a_gen_progress.update_progress(col_index)
    a_gen_progress.finish()
else:
    loaded_data = sio.loadmat(args.prefix+'/route_assignment_matrices.mat')
    A = loaded_data['A']
    sensors = loaded_data['b']

# TODO remove first row of A before saving
# TODO N = np.sum(U,axis=0)
# TODO save N as well

sio.savemat(data_prefix+'/route_assignment_matrices.mat', {'A':A, 'U':x_matrix.U, 'x':x_matrix.x, 'b':sensors})
