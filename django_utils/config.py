ACCEPTED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'WARN']

DATA_DIR = '/home/lei/traffic/datasets/Phi' # FIXME replace with your data path
WAYPOINTS_DIRECTORY = DATA_DIR + '/waypoints/ISTTT-largerbbox'
EXPERIMENT_MATRICES_DIR = 'experiment_matrices'
ESTIMATION_INFO_DIR = 'estimation_info'
WAYPOINTS_FILE = 'waypoints-950.pkl'
WAYPOINT_DENSITY = 950
WAYPOINT_DENSITIES = [3800,3325,2850,2375,1900,1425,950,713,475,238]
canonical_projection = 4326
google_projection = 3857#900913 # alternatively 3857
EPSG32611 = 32611
PLOT_DIR = '/home/lei/traffic/plots'

NUM_ROUTES_PER_OD = 3
SIMILARITY_FACTOR = .8
import os
# The directory must exist for other parts of this application to function properly
assert(os.path.isdir(DATA_DIR))
