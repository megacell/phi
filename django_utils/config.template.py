ACCEPTED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'WARN']

# Directory Setup
DATA_DIR = '/home/chenyang/src/traffic/datasets/Phi' # FIXME replace with your data path
EXPERIMENT_MATRICES_DIR = 'experiment_matrices'
ESTIMATION_INFO_DIR = 'estimation_info'
PLOT_DIR = DATA_DIR+'/plots' #your plot dir

# Links setup
LINKS_FILES = DATA_DIR +'/LA_shps/links/LA_network_links_V2'

# Trajectories setup
TRAJECTORY_CSV = DATA_DIR + '/trajectories/OD_500k.csv'

# Various projections
canonical_projection = 4326
google_projection = 3857 #900913 # alternatively 3857
EPSG32611 = 32611

# Waypoints setup
WAYPOINTS_DIRECTORY = DATA_DIR + '/att_data/'
WAYPOINTS_FILE = 'att-waypoints.pkl'
WAYPOINT_DENSITY = 1
SINGLE_WAYPOINT = False
WAYPOINT_DENSITIES = [3800,3325,2850,2375,1900,1425,950,713,475,238,0]


NUM_ROUTES_PER_OD = 3
SIMILARITY_FACTOR = .8
import os

# The directory must exist for other parts of this application to function properly
assert(os.path.isdir(DATA_DIR))
assert(os.path.isdir(PLOT_DIR))
