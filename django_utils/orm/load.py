import os
import csv
import logging
import pickle
import json
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import Point, LineString
from collections import defaultdict
from django.db import transaction
from django.db import connection
import scipy.io as sio
import numpy as np
from models import Sensor, Origin, Route, Waypoint, MatrixTaz, ExperimentRoute, Experiment, ExperimentSensor
from lib.console_progress import ConsoleProgress
from lib import google_lines
import models
import kmzsensorfilereader as kmz
import django_utils.config as config
logging.basicConfig(level=logging.DEBUG)

canonical_projection = 4326
google_projection = 3857#900913 # alternatively 3857

N_TAZ = 321
# FIXME poor practice
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = config.DATA_DIR
data_prefix = "%s" % DATA_PATH #TODO(syadlowsky): make these consistent

origin_shp = os.path.abspath('%s/origin/ods.shp' % DATA_PATH)

def load_origins(verbose=True):
    lm = LayerMapping(Origin, origin_shp, models.origin_mapping,
            encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)
    for o in Origin.objects.all():
        o.geom_dist = o.geom.clone()
        o.geom_dist.srid = canonical_projection
        o.geom_dist.transform(google_projection)
        o.save()
        logging.info("Saved origin with distance.")

sensor_mapping = {
    'pems_id': 'ID',
    'freeway': 'Fwy',
    'direction': 'Dir',
    'district_id': 'District',
    'county_id': 'County',
    'city_id': 'City',
    'state_pm': 'State_PM',
    'absolute_pm': 'Abs_PM',
    'sensor_length': 'Length',
    'sensor_type': 'Type',
    'lanes': 'Lanes',
    'name': 'Name',
    'user_id_1': 'User_ID_1',
    'user_id_2': 'User_ID_2',
    'user_id_3': 'User_ID_3',
    'user_id_4': 'User_ID_4',
    'shape_length': 'Shape_Leng',
    'shape_area': 'Shape_Area',
    'cnty': 'CNTY',
    'taz_id': 'TAZ_ID',
    'pop_20': 'POP20',
    'hh_20': 'HH20',
    'emp_20': 'EMP20',
    'pop_35': 'POP35',
    'hh_35': 'HH35',
    'emp_35': 'EMP35',
    'cnty_1': 'CNTY_1',
    'taz_id_1': 'TAZ_ID_1',
    'pop_08': 'POP08',
    'hh_08': 'HH08',
    'emp_08': 'EMP08',
}
sensor_mapping_reverse = {v:k for k,v in sensor_mapping.iteritems()}

def _remap_column_names(row):
    params = {sensor_mapping_reverse[k]: v for k, v in row.iteritems() if sensor_mapping_reverse.has_key(k)}
    params['location'] = Point(float(row['Longitude']), float(row['Latitude']), srid=canonical_projection)
    params['location_dist'] = Point(float(row['Longitude']), float(row['Latitude']), srid=canonical_projection)
    params['location_dist'].transform(google_projection)
    return params

def _save_sensor(params):
    try:
        sensor = Sensor(**params)
        sensor.save()
    except:
        print params
        raise

def import_sensors(verbose=True):
    Sensor.objects.all().delete()
    for row in csv.DictReader(open("{0}/sensors/sensors.csv".format(DATA_PATH))):
        row = {k: v.strip() for k, v in row.iteritems() if v.strip()}
        params = _remap_column_names(row)
        params['road_type']='Freeway'
        _save_sensor(params)
    for row in kmz.getArterialSensors():
        params = _remap_column_names(row)
        params['road_type']='Arterial'
        _save_sensor(params)

def import_lookup(verbose=True):
    waypoints = pickle.load(open("{0}/lookup.pickle".format(DATA_PATH)))
    ac = transaction.get_autocommit()
    transaction.set_autocommit(False)
    for matrix_id, taz_id in waypoints.iteritems():
        mt = MatrixTaz(matrix_id=matrix_id, taz_id=taz_id)
        mt.save()
    transaction.commit()
    transaction.set_autocommit(ac)

def load_waypoints_file(filepath, density_id):
    waypoints = pickle.load(open("{0}/{1}".format(config.WAYPOINTS_DIRECTORY, filepath)))
    #ac = transaction.get_autocommit()
    #transaction.set_autocommit(False)
    for category, locations in waypoints.iteritems():
        for location in locations:
            pt = Point(tuple(location), srid=canonical_projection)
            wp = Waypoint(location=pt, location_dist=pt.transform(google_projection, clone=True), category=category, density_id=density_id)
            wp.save()
    #transaction.commit()
    #transaction.set_autocommit(ac)

def import_waypoints(verbose=True):
    Waypoint.objects.all().delete()
    if config.SINGLE_WAYPOINT:
        density = config.WAYPOINT_DENSITY
        filename = config.WAYPOINTS_FILE
        load_waypoints_file(filename, density)
    else:
        density = config.WAYPOINT_DENSITIES
        files = ["waypoints-{0}.pkl".format(d) for d in density]
        for f,d in zip(files,density):
            if d == 0:
                continue
            load_waypoints_file(f, d)


def find_route_by_origin_destination_route_index(o, d, idx):
    r = Route.objects.raw("SELECT r.* FROM orm_route r INNER JOIN orm_matrixtaz t ON r.origin_taz = t.taz_id INNER JOIN orm_matrixtaz s ON r.destination_taz = s.taz_id WHERE t.matrix_id = %s AND s.matrix_id = %s AND r.od_route_index = %s LIMIT 1;", (o, d, idx))
    return r[0]

def import_experiment_sensors(description):
    """Assumes you have an experiment with that description"""
# Load b vector from MAT file
    route_split = sio.loadmat(open("{0}/experiment_matrices/route_assignment_matrices_ntt.mat".format(DATA_PATH)))
    b = np.squeeze(np.asarray(route_split['b']))
    ac = transaction.get_autocommit()
    transaction.set_autocommit(False)
# Find experiment
    experiment = Experiment.objects.get(description=description)
# Load CSV, enumerate over lines
    for idx, row in enumerate(csv.DictReader(open("{0}/sensors.csv".format(DATA_PATH)))):
        sensor = Sensor.objects.get(pems_id=row['ID'], road_type='Freeway')
        es = ExperimentSensor(sensor=sensor, value=b[idx], experiment=experiment, vector_index=idx)
        es.save()
# For each line, find value in b, and then create the ExperimentSensor with that vector_index cross-checked by PEMS id
    transaction.commit()
    transaction.set_autocommit(ac)

def import_experiment(filename, description):
    back_map = pickle.load(open(filename))
    condensed_map = defaultdict(list)
    for k, v in back_map.iteritems():
        condensed_map[v].append(k)
    ac = transaction.get_autocommit()
    transaction.set_autocommit(False)
    for k, v in condensed_map.iteritems():
        o, d = k
        for idx, rt in enumerate(v):
            route = find_route_by_origin_destination_route_index(o, d, idx)
            er = ExperimentRoute(route=route, vector_index=rt, description=description, true_split=False)
            er.save()
            er = ExperimentRoute(route=route, vector_index=rt, description=description, true_split=True)
            er.save()
    transaction.commit()
    transaction.set_autocommit(ac)

def import_experiment_data(description):
    route_split = sio.loadmat(open("{0}/outputSmallData.mat".format(DATA_PATH)))
    b = np.squeeze(np.asarray(route_split['x_true']))
    sql = """
    UPDATE orm_experimentroute AS er SET
        value = %s
    WHERE vector_index = %s AND er.description = %s AND er.true_split=TRUE;
    """
    values = [(v,k,description) for k, v in enumerate(b)]
    ac = transaction.get_autocommit()
    transaction.set_autocommit(False)
    cursor = connection.cursor()
    cursor.executemany(sql, values)
    transaction.commit()
    transaction.set_autocommit(ac)
    b = np.squeeze(np.asarray(route_split['xLBFGS']))
    sql = """
    UPDATE orm_experimentroute AS er SET
        value = %s
    WHERE vector_index = %s AND er.description = %s AND er.true_split=FALSE;
    """
    values = [(v,k,description) for k, v in enumerate(b)]
    ac = transaction.get_autocommit()
    transaction.set_autocommit(False)
    cursor = connection.cursor()
    cursor.executemany(sql, values)
    transaction.commit()
    transaction.set_autocommit(ac)

def import_routes():
    taz_lookup = pickle.load(open(data_prefix+'/lookup.pickle'))

    def compute_route_time(route):
        travel_time = 0
        for leg in route['legs']:
            travel_time += leg['duration']['value']
        return travel_time

    def getRoutesAndSave(o, d):
        data = json.load(open(data_prefix+'/data/%s_%s.json' % (o, d)))
        for route_index, route in enumerate(data['routes']):
            gpolyline = route['overview_polyline']['points']
            linestring = google_lines.decode_line(gpolyline)
            linestring.set_srid(canonical_projection)
            linestring_dist = linestring.clone()
            linestring_dist.transform(google_projection)
            route_object = Route(geom=linestring, geom_dist=linestring_dist, \
                    summary=route['summary'], origin_taz=taz_lookup[o], \
                    destination_taz=taz_lookup[d], \
                    travel_time=compute_route_time(route), \
                    od_route_index=route_index, \
                    json_contents=json.dumps(route))
            route_object.save()

    # Get list of origins
    files = os.listdir(data_prefix+'/data')
    origins = {}
    for file in files:
      file = file.replace('.json', '')
      o, d = map(int, file.split('_'))
      if not o in origins:
        origins[o] = {}
      if not d in origins[o]:
        origins[o][d] = []

    # Load all routes from origins
    gen_tt = ConsoleProgress(N_TAZ*(N_TAZ-1), message="Saving to database.")
    for index_o, o in enumerate(origins):
      for index_d, d in enumerate(origins[o]):
        getRoutesAndSave(o, d)
        gen_tt.increment_progress()
    gen_tt.finish()

def import_experiment_from_agent_google_match():
    import uuid
    from django.db import transaction
    from phidb.db.backends.postgresql_psycopg2.base import *
    from django.db import connection
    import numpy as np

    with server_side_cursors(connection):
        cursor = connection.cursor()

        query = """
        """
        cursor.execute(query)
        results = [row for row in cursor]
        results = [(i,o,d,r,v) for (i,o,d,r,v) in results]
        print 'len: %s' % len(results)

    description = 'agents_google_match'
    ac = transaction.get_autocommit()
    transaction.set_autocommit(False)
    for j,(i,o,d,r,v) in enumerate(results):
        er = ExperimentRoute(route=i, vector_index=j, value=v,
                description=description, true_split=True)
        er.save()
    transaction.commit()
    transaction.set_autocommit(ac)
def import_all():
    import_sensors()
    load_origins()
    #import_lookup()
    #import_routes()
    import_waypoints()
