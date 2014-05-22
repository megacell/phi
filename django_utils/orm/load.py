import os
import csv
import logging
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import Point, LineString
from models import Sensor, Origin
import models

DATA_PATH = '/home/steve/megacell/datasets'

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
