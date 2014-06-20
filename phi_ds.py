import pickle
from lib.console_progress import ConsoleProgress

class Phi:
    data_prefix = ""

    def __init__(self, data=None, generate_phi=None):
        self.info = data
        self.generate_phi = generate_phi

    def set_data(self, data):
        self.info = data

    def data(self):
        if self.info:
            return self.info
        else:
            load_phi_progress = ConsoleProgress(1, message="Loading phi")
            if generate_phi:
# TODO: replace with experiment id
                self.info = generate_phi.phi_generation_sql(1)
            else:
                self.info = pickle.load(open(self.__class__.data_prefix+'/phi.pickle'))
            load_phi_progress.finish()
            return self.info
