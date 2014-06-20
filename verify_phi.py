import numpy as np
import pickle
from scipy.sparse import csr_matrix, lil_matrix
from lib.console_progress import ConsoleProgress
import scipy.io as sio
import csv
import math
import logging

logging.basicConfig(level=logging.DEBUG)

data_prefix = ""
N_TAZ = 321
N_TAZ_CONDENSED = 150
N_ROUTES = 280691
N_ROUTES_CONDENSED = 60394
N_SENSORS = 1033
FIRST_ROUTE = 0

data = pickle.load(open('data/phi.pickle'))
phi_db = pickle.load(open('data/phi_condensed1402867630.8_db.pickle'))['phi']

phi_errors = 0
x_gen_progress = ConsoleProgress(N_TAZ * N_TAZ, message="Comparing phi")
for i in np.arange(N_TAZ):
    for j in np.arange(N_TAZ):
        if data[i].get(j):
            if data[i][j]:
                if data[i][j] != map(lambda x: sorted(x[1]), phi_db[(i, j)].iteritems()):
                    phi_errors += 1
                    print data[i][j]
                    print phi_db[(i, j)]
                    if phi_errors >= 10:
                        exit()
                x_gen_progress.increment_progress()
x_gen_progress.finish()
