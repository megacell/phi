__author__ = 'lei'
import scipy.io as sio

class MatrixGenerator:
    def generate_matrices(self):
        pass
    def save_matrices(self, filename):
        if (self.matrices == None):
            self.generate_matrices()
        sio.savemat(filename, self.matrices)