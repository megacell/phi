import numpy as np
import pickle
from scipy.sparse import csr_matrix, lil_matrix
from lib.console_progress import ConsoleProgress
import scipy.io as sio
import csv
import math

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-float(x)))

class XMatrix:
    data_prefix = ""
    N_TAZ = 321
    N_TAZ_CONDENSED = 75
    N_ROUTES = 280691
    N_ROUTES_CONDENSED = 60394
    N_SENSORS = 1033
    FIRST_ROUTE = 0

    def __init__(self, compute=True, phi=None, condensed_map=None, use_travel_times=False):
        if compute:
            # Load the data.
            data_progress = ConsoleProgress(1, message="Loading phi")
            self.condensed_map = condensed_map
            data = pickle.load(open(self.__class__.data_prefix+'/phi.pickle'))
            phi.set_data(data)
            data_progress.finish()
            self.generate_routing_matrix(data, use_travel_times)
            sio.savemat(self.__class__.data_prefix+'/X_matrix.mat', {
                'X' : self.X,
                'x' : self.x,
                'U' : self.U
            })
        else:
            x_load_progress = ConsoleProgress(1, message="Loading X matrix from file")
            loaded_data = sio.loadmat(self.__class__.data_prefix+'/X_matrix.mat')
            self.X = loaded_data['X']
            self.U = loaded_data['U']
            self.x = loaded_data['x']
            x_load_progress.finish()
        self.phi = phi

    def generate_od_travel_time_pairs(self):
        gen_tt = ConsoleProgress(self.N_TAZ, message="Loading travel times")
        od_pair_matrix = [[{} for x in range(self.N_TAZ)] for y in range(self.N_TAZ)]
        with open(self.__class__.data_prefix+'/travel_times.csv') as fopen:
            reader = csv.reader(fopen,delimiter=',')
            # skip reading first line
            firstline = fopen.readline()
            for row in reader:
                od_pair_matrix[int(row[0])][int(row[1])][int(row[2])] = float(int(row[3]))
                gen_tt.update_progress(int(row[0]))
        gen_tt.finish()
        return od_pair_matrix

    def generate_routing_matrix(self, data, use_travel_times):
        """
        Given the route index associated with each OD pair, generate a routing matrix.
        """
        self.X = lil_matrix((self.N_SENSORS, self.N_TAZ*self.N_TAZ))
        self.x = np.zeros(self.N_ROUTES_CONDENSED)
        x_ind = 0
        if use_travel_times:
            od_pair_travel_times = self.generate_od_travel_time_pairs()
        x_gen_progress = ConsoleProgress(self.N_ROUTES, message="Generating X and U matrices")
        self.U = lil_matrix((self.N_TAZ_CONDENSED*(self.N_TAZ_CONDENSED-1), self.N_ROUTES_CONDENSED))
        # For efficiency, the if statement is surrounding these loops so it doesn't check every iteration
        if use_travel_times:
            for i in np.arange(self.N_TAZ):
                for j in np.arange(self.N_TAZ):
                    if data[i].get(j):
                        if data[i][j]:
                            travel_times = od_pair_travel_times[i][j]
                            mean_tt = np.mean(travel_times.values())
                            std_tt = np.std(travel_times.values())
                            if std_tt == 0:
                                std_tt = 1
                            travel_times = {rt : (float(tt-mean_tt) / std_tt) for rt, tt in travel_times.items()}
                            travel_times = {rt : sigmoid(tt) for rt, tt in travel_times.items()}
                            normalizer = float(sum(travel_times.values()))
                            travel_times = {rt : float(tt)/normalizer for rt, tt in travel_times.items()}
                            for route, sensors in enumerate(data[i][j]):
                                tt = travel_times[route]
                                for s in sensors:
                                    self.X[s,i*self.N_TAZ+j] += tt
                                if i in self.condensed_map and j in self.condensed_map:
                                    i_ind = self.condensed_map[i]
                                    j_ind = self.condensed_map[j]
                                    self.x[x_ind] = tt
                                    row_index = i_ind*(self.N_TAZ_CONDENSED-1)+j_ind
                                    if j_ind > i_ind:
                                        row_index -= 1
                                    self.U[row_index, x_ind] = 1
                                    x_ind = x_ind + 1
                                x_gen_progress.increment_progress()
        else:
            for i in np.arange(self.N_TAZ):
                for j in np.arange(self.N_TAZ):
                    if data[i].get(j):
                        if data[i][j]:
                            for route, sensors in enumerate(data[i][j]):
                                if route == self.FIRST_ROUTE:
                                    for s in sensors:
                                        self.X[s,i*self.N_TAZ+j] = 1
                                    self.x[x_ind] = 1
                                if i in self.condensed_map and j in self.condensed_map:
                                    i_ind = self.condensed_map[i]
                                    j_ind = self.condensed_map[j]
                                    row_index = i_ind*(self.N_TAZ_CONDENSED-1)+j_ind
                                    if j_ind > i_ind:
                                        row_index -= 1
                                    self.U[row_index, x_ind] = 1
                                    x_ind += 1
                                x_gen_progress.increment_progress()
        x_gen_progress.finish()
