import csv
import django_utils.config as config
from django.db import connection
import cStringIO

class TrajectoryLoader:
    db_ids = ['agent_id', 'commute_direction', 'orig_TAZ', 'dest_TAZ', 'link_ids']
    ids = ['agent_id', 'commute_direction', 'orig_TAZ', 'dest_TAZ', 'route_string']
    fs = [
        lambda x: int(x),
        lambda x: int(x),
        lambda x: int(float(x)),
        lambda x: int(float(x)),
        lambda x: '{' + ','.join([str(int(i)) for i in x.strip().split(' ')]) + '}'
    ]

    def __init__(self, connection, csvfile):
        self.connection = connection
        self.csv_file = csv.DictReader(csvfile)

    @staticmethod
    def _create_trajectory_string(trajectory_row):
        t = '\t'.join([str(f(trajectory_row[id])) for id, f in zip(TrajectoryLoader.ids,TrajectoryLoader.fs)])
        return t

    def _add_trajectories(self, trajectories, cursor):
        # dumping everything into this string and using the copy_from method is substantially faster than inserting
        # values one by one into the db
        sio = cStringIO.StringIO('\n'.join([TrajectoryLoader._create_trajectory_string(t) for t in trajectories]))
        cursor.copy_from(sio, 'experiment2_trajectories')

    # will clear old values in the db and replace them with new values provided in the file
    def load(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            DROP TABLE IF EXISTS experiment2_trajectories;
            CREATE TABLE experiment2_trajectories (
            agent_id integer,
            commute_direction integer,
            orig_TAZ float,
            dest_TAZ float,
            link_ids int[]
            );
            CREATE INDEX ON experiment2_trajectories (orig_TAZ);
            CREATE INDEX ON experiment2_trajectories (dest_TAZ);'''
        )
        self._add_trajectories(self.csv_file, cursor)
def load():
    import timeit
    tic = timeit.default_timer()
    with open(config.DATA_DIR + 'trajectories/OD_500k.csv') as odcsv:
        loader = TrajectoryLoader(connection, odcsv)
        loader.load()
    toc = timeit.default_timer()
    print (toc - tic)

if __name__ == "__main__":
    load()
