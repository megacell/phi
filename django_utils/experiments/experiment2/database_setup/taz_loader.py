from django_utils import config as config
from django.contrib.gis.geos import Polygon
from django.db import connection
from pdb import set_trace as T

import cStringIO
import shapefile
import pickle

def load_taz(connection, filename):
    id_to_geom = pickle.load(open(filename))
    data = ['\t'.join([str(taz_id), geom.ewkt]) for taz_id, geom in id_to_geom.items()]
    data = '\n'.join(data)
    sio = cStringIO.StringIO(data)
    cursor = connection.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS taz_geometry CASCADE;
        CREATE TABLE taz_geometry (
        taz_id integer,
        geom geometry(POLYGON)
        );'''
    )
    cursor.copy_from(sio, 'taz_geometry')

def load():
    load_taz(connection, config.TAZ_FILE)

if __name__ == '__main__':
    load()
