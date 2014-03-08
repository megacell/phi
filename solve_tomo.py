"""
Solve network tomography problem with radiation model as a baseline
"""

import sys
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
Nroutes = 280691
Nsens = 1033

# Load the data.
data = pickle.load(open('phi.pickle'))

# Choose origin.
origin = 123
destination = 10

# Lets have a look at the first route leaving this origin.
route = 0

# It intersects the following sensors.
# sensors = data[origin][destination][route]
# print "%s: Data loaded, sample path: %s" % (str(time.time()-t0), str(sensors))

# Routing matrix for tomogravity model
X = lil_matrix((Nsens, Ntaz*Ntaz))
x = np.zeros(Nroutes)
x_ind = 0
print
for i in np.arange(Ntaz):
    for j in np.arange(Ntaz):
        if data[i].get(j): 
            if data[i][j]:              
                for ind, routes in enumerate(data[i][j]):
                    if ind == 0:
                        for r in routes:
                            X[r,i*Ntaz+j] = 1
                    x_ind = x_ind + 1
                    sys.stdout.write("\r{0:.2f}%%".format(100*float(x_ind)/Nroutes))
                    sys.stdout.flush()
#sio.savemat("x.mat", {'x':x})

sio.savemat('X_matrix.mat', {'X':X})
# X = pickle.load(open('X_matrix.pickle'))
print "%s: Routing matrix X completed" % str(time.time()-t0)  
    
# Read pre-computed trip counts for all OD pairs (simulated with radiation model)
rad, TAZ = np.zeros((321,321)), np.zeros(321)
with open('trips.csv') as file:
  reader = csv.reader(file,delimiter=',')
  firstline = file.readline()   # skip the first line
  for row in reader:
    rad[int(row[2]),int(row[3])] = int(float(row[6]))        

print "%s: Heuristic OD loaded" % str(time.time()-t0)


radflow = rad.reshape((Ntaz*Ntaz,1))


Use_Real_Sensors = False

if Use_Real_Sensors:

  # Real count data from PEMS
  day_num = 3
  sensors, nocounts, yescounts = np.zeros((1033,1)), [], []
  with open('sensor_counts2.csv') as file:
    reader = csv.reader(file,delimiter=',')
    firstline = file.readline()   # skip the first line
    for row in reader:
      if not row[day_num]=='nan':
          sensors[int(row[0]),0] = int(float(row[day_num]))
          yescounts.append(int(row[0]))
      else:
          nocounts.append(int(row[0]))
    
  
  radflow = (sensors.sum()/np.sum(X*radflow))*radflow
               
               
if not Use_Real_Sensors:    
  # right side for the tomogravity model + noise 
  sensors = X*(radflow + 100*np.random.rand((Ntaz*Ntaz),1))    
  yescounts = np.arange(Nsens)
  

##    
# wlse_tomogravity solved with sparse least squares   
#
bw = sensors - X*radflow
Xcsr = csr_matrix(X)
tw = lsqr(Xcsr[yescounts,:], bw[yescounts], damp = 100)[0]

# transform tw back to t
t = radflow[:,0] + tw
 
print "%s: LSQR solved" % str(time.time()-t0)    

### 
##  Pseudo-inv via SVD
##
#u,s,v = svds(Xcsr[yescounts,:],500)
#invs = np.diag(1/s)
#invX = csr_matrix(np.dot(v.T,np.dot(invs,u.T)))
#tw = invX*bw[yescounts,:]
#
#print "%s: SVD solved" % str(time.time()-t0)  
#
## transform tw back to t
#t_svd = radflow[:,0] + tw

## back-substitution to check the results
c_lsqr = X*t
#c_svd = X*t_svd
c_rad = X*radflow[:,0]

# plot LSQR solution vs sensors
plt.plot(c_lsqr,sensors,'ro')
#plt.plot(c_svd,sensors,'bo')

flow_model = np.array(t.reshape((Ntaz,Ntaz)))

lookup = pickle.load(open('lookup.pickle'))
rlookup = {}
for index in lookup:
  rlookup[lookup[index]] = index

data = []
with open('radiation_results.csv') as fopen:
  for row in fopen:
    data.append(map(float, row.strip().split(',')[:-1]))

pop = {}
sf = shapefile.Reader("data/ods.shp")
records = sf.records()
for i in range(len(records)):
  pop[records[i][3]] = float(records[i][4])
  
A = lil_matrix((Nsens, Nroutes))
U = lil_matrix((Ntaz*Ntaz, Nroutes))

route_phi = pickle.load(open('phi.pickle'))
col_index = 0
with open('trips_model.csv', 'w') as fout:
  fout.write('origin,destination,origin_index,destination_index,prob,pop20,trips\n')
  for i in range(len(data)-1):
    for j in range(len(data)-1):
      if i > 0 and j > 0 and i != j:
        fout.write('%s,%s,%s,%s,%s,%s,%s\n' % (data[0][i], data[j][0], rlookup[data[0][i]], rlookup[data[j][0]], data[i][j], pop[data[0][i]], max(0, flow_model[rlookup[data[0][i]], rlookup[data[j][0]]])))
        origin, destination = rlookup[data[0][i]], rlookup[data[j][0]]
        routes = route_phi[origin][destination]
        for route_index, row_indices in enumerate(routes):
            row_index = (origin*Ntaz + destination)
            U[row_index, col_index] = 1
            for row_index in row_indices:
                A[row_index, col_index] = max(0, flow_model[rlookup[data[0][i]], rlookup[data[j][0]]])
            col_index = col_index + 1

sio.savemat("rhs_matrices.mat", {'A':A, 'U':U, 'x':x})
