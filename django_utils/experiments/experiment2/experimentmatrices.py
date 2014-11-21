__author__ = 'lei'
import scipy.io as sio

class ExperimentMatrices:
    def __init__(self, A, b, x_true, U, f, route_table):
        self.A = A
        self.b = b
        self.x_true = x_true
        self.U = U
        self.f = f
        self.route_table = route_table

    def save_matrices(self, filename):
        sio.savemat(filename, {'A':self.A, 'U':self.U, 'x_true':self.x_true, 'b':self.b, 'f':self.f, 'route_table':self.route_table})

    def load_matrices(self, filename):
        matrices = sio.loadmat(filename)

        if 'A' in matrices.keys():
            self.A = matrices['A']

        if 'b' in matrices.keys():
            self.b = matrices['b']

        if 'x_true' in matrices.keys():
            self.x_true = matrices['x_true']

        if 'U' in matrices.keys():
            self.U = matrices['U']

        if 'f' in matrices.keys():
            self.f = matrices['f']

        if 'route_table' in matrices.keys():
            self.route_table = matrices['route_table']

    def __repr__(self):
        s = ''
        s += "A shape:" +str(self.A.shape)
        s += "U shape:" + str(self.U.shape)
        s += "x_true shape:" + str(self.x_true.shape)
        s += "b shape:" + str(self.b.shape)
        return s