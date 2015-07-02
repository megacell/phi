import psycopg2
import config
import pickle

# Set when loading data
ATT_WAYPOINT_DENSITY = 1

class MatrixGenerator():
    def __init__():
        self.conn = psycopg2.connect(database='geodjango', user='megacell')
        self.params = { 'num_routes': num_routes
                      , 'density'   :ATT_WAYPOINT_DENSITY}
        self.sensors = pickle.load(open(config.PEMS_LINKS))

    def x_gen(self):
        return

    def A_gen(self):
        return
