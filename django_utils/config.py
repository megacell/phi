ACCEPTED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'WARN']

DATA_DIR = '/home/lei/traffic/datasets/Phi' # FIXME replace with your data path
EXPERIMENT_MATRICES_DIR = 'experiment_matrices'
ESTIMATION_INFO_DIR = 'estimation_info'

canonical_projection = 4326
google_projection = 3857#900913 # alternatively 3857
EPSG32611 = 32611

import os
# The directory must exist for other parts of this application to function properly
assert(os.path.isdir(DATA_DIR))
