import os
import csv
import logging
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.geos import Point, LineString
from models import WorldBorder, Sensor

DATA_PATH = '/home/steve/megacell/datasets'

world_mapping = {
    'fips' : 'FIPS',
    'iso2' : 'ISO2',
    'iso3' : 'ISO3',
    'un' : 'UN',
    'name' : 'NAME',
    'area' : 'AREA',
    'pop2005' : 'POP2005',
    'region' : 'REGION',
    'subregion' : 'SUBREGION',
    'lon' : 'LON',
    'lat' : 'LAT',
    'mpoly' : 'MULTIPOLYGON',
}

world_shp = os.path.abspath('/home/steve/megacell/code/django_utils/world/data/TM_WORLD_BORDERS-0.3.shp')

def run(verbose=True):
    lm = LayerMapping(WorldBorder, world_shp, world_mapping,
                      transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)

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
        params['location'].transform(900913)
        try:
            sensor = Sensor(**params)
            sensor.save()
        except:
            print params
            raise
