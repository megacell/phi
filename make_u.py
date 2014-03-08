"""
Solve network tomography problem with radiation model as a baseline
"""

import csv
import pickle
import numpy as np

import time

import shapefile

from scipy.sparse import csr_matrix, lil_matrix
from scipy.sparse.linalg import lsqr, lsmr, svds

from scipy.sparse import hstack

from matplotlib import pyplot as plt

import scipy.io as sio

def add_data_path(original_function):
    # make a new function that prints a message when original_function starts and finishes
    def new_function(*args, **kwargs):
        args = list(args)
        args[0] = "data/" + args[0]
        args = tuple(args)
        return original_function(*args, **kwargs)
 
    return new_function

open = add_data_path(open)

t0 = time.time()

Ntaz = 321
Nroutes = 3
Nsens = 1033

lookup = pickle.load(open('lookup.pickle'))
rlookup = {}
for index in lookup:
  rlookup[lookup[index]] = index

data = []
with open('radiation_results.csv') as fopen:
  for row in fopen:
    data.append(map(float, row.strip().split(',')[:-1]))

U = lil_matrix((Ntaz*Ntaz, Nroutes*Ntaz*Ntaz))

route_phi = pickle.load(open('phi.pickle'))
col_index = 0
for i in range(len(data)-1):
  for j in range(len(data)-1):
    if i > 0 and j > 0 and i != j:
      origin, destination = rlookup[data[0][i]], rlookup[data[j][0]]
      row_index = (origin*Ntaz + destination)
      routes = route_phi[origin][destination]
      for route_index, row_indices in enumerate(routes):
          col_index = Nroutes*row_index + route_index
          U[row_index, col_index] = 1
          col_index = col_index + 1

sio.savemat("u.mat", {'U':U})

# Routing matrix for tomogravity model
#A = lil_matrix((Nsens, Ntaz*Ntaz))
#for i in np.arange(Ntaz):
#    for j in np.arange(Ntaz):
#        if data[i].get(j): 
#            if data[i][j]:              
#                for r in data[i][j][0]:
#                  A[r,i*Ntaz+j] = 1
