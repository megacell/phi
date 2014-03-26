import pickle
from lib.console_progress import ConsoleProgress

class Phi:
    data_prefix = ""

    def __init__(self, data=None):
        self.info = data

    def set_data(self, data):
        self.info = data

    def data(self):
        if self.info:
            return self.info
        else:
            load_phi_progress = ConsoleProgress(1, message="Loading phi")
            self.info = pickle.load(open(self.__class__.data_prefix+'/phi.pickle'))
            load_phi_progress.finish()
            return self.info
