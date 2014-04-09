import numpy as np
import pickle
from scipy.sparse import csr_matrix, lil_matrix
from lib.console_progress import ConsoleProgress
import scipy.io as sio
import csv
import math

class RadiationModel:
    data_prefix = ""
    N_TAZ = 321
    N_TAZ_CONDENSED = 150
    N_ROUTES = 280691
    N_ROUTES_CONDENSED = 60394
    N_SENSORS = 1033
    FIRST_ROUTE = 0

    def __init__(self, compute_trip_counts=False):
        self.flow = None
        if compute_trip_counts:
            raise NotImplementedError
        else:
            self.rad, TAZ = np.zeros((self.N_TAZ,self.N_TAZ)), np.zeros(self.N_TAZ)
            load_radiation_progress = ConsoleProgress(self.N_TAZ*self.N_TAZ, message="Loading radiation model heuristic")
            with open(self.data_prefix+'/trips.csv') as file:
              reader = csv.reader(file,delimiter=',')
              firstline = file.readline()   # skip the first line
              for prog, row in enumerate(reader):
                self.rad[int(row[2]),int(row[3])] = int(float(row[6]))
                load_radiation_progress.update_progress(prog)
            load_radiation_progress.finish()

    def as_flow(self):
        if self.flow is None:
            self.flow = self.rad.reshape((self.N_TAZ*self.N_TAZ, 1))
        return self.flow
