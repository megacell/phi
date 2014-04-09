import numpy as np
import pickle
from scipy.sparse import csr_matrix, lil_matrix
from lib.console_progress import ConsoleProgress
import scipy.io as sio
import csv
import math

class Sensors:
    data_prefix = ""
    N_TAZ = 321
    N_TAZ_CONDENSED = 150
    N_ROUTES = 280691
    N_ROUTES_CONDENSED = 60394
    N_SENSORS = 1033
    FIRST_ROUTE = 0

    def __init__(self, use_real_sensors=False, x_matrix=None, radflow=None):
        self.flow = None

        if use_real_sensors:
          # Real count data from PEMS
          day_num = 3
          self.sensors, self.yescounts = np.zeros((1033,1)), []
          with open(data_prefix+'/sensor_counts2.csv') as file:
            reader = csv.reader(file,delimiter=',')
            firstline = file.readline()   # skip the first line
            for row in reader:
              if not row[day_num]=='nan':
                  self.sensors[int(row[0]),0] = int(float(row[day_num]))
                  self.yescounts.append(int(row[0]))
          self.radflow = (self.sensors.sum()/np.sum(x_matrix.X*radflow))*radflow
        else:
          # right side for the tomogravity model + noise 
          self.sensors = x_matrix.X*(radflow + 100*np.random.rand((self.N_TAZ*self.N_TAZ),1))
          self.yescounts = np.arange(self.N_SENSORS)
          self.radflow = radflow

    def get_flow(self):
        return self.radflow
