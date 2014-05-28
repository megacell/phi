import os
import csv
import logging
import pickle
import json
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import Point, LineString
from django.db import transaction
from models import Sensor, Origin, Route, Waypoint
from lib.console_progress import ConsoleProgress
from lib import google_lines
import models

logging.basicConfig(level=logging.DEBUG)

N_TAZ = 321
DATA_PATH = '/home/steve/megacell/datasets'
data_prefix = "%s/Phi" % DATA_PATH #TODO(syadlowsky): make these consistent

origin_shp = os.path.abspath('/home/steve/megacell/code/django_utils/orm/data/ods.shp')

def load_origins(verbose=True):
    lm = LayerMapping(Origin, origin_shp, models.origin_mapping,
            encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)
    for o in Origin.objects.all():
        o.geom_dist = o.geom.clone()
        o.geom_dist.srid = 4326
        o.geom_dist.transform(900913)
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

def import_sensors(verbose=True):
    for row in csv.DictReader(open("{0}/Phi/sensors.csv".format(DATA_PATH))):
        row = {k: v.strip() for k, v in row.iteritems() if v.strip()}
        params = {sensor_mapping_reverse[k]: v for k, v in row.iteritems() if sensor_mapping_reverse.has_key(k)}
        params['location'] = Point(float(row['Longitude']), float(row['Latitude']), srid=4326)
        params['location_dist'] = Point(float(row['Longitude']), float(row['Latitude']), srid=4326)
        params['location_dist'].transform(900913)
        try:
            sensor = Sensor(**params)
            sensor.save()
        except:
            print params
            raise

def import_waypoints(verbose=True):
    waypoints = pickle.load(open("{0}/Phi/waypoints.pkl".format(DATA_PATH)))
    ac = transaction.get_autocommit()
    transaction.set_autocommit(False)
    for category, locations in waypoints.iteritems():
        for location in locations:
            pt = Point(tuple(location), srid=4326)
            wp = Waypoint(location=pt, location_dist=pt.transform(900913, clone=True), category=category)
            wp.save()
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
            linestring.set_srid(4326)
            linestring_dist = linestring.clone()
            linestring_dist.transform(900913)
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
