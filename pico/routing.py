import os
import pico
import requests
import pickle
import scipy.io as sio
import numpy as np
from django.contrib.gis.geos import Point, LineString

DATA_PATH = '/home/steve/megacell/datasets'
FUZZY_DIST = 10

def sensors(point_list):
    points = pickle.load(open("{0}/Phi/sensors.pickle".format(DATA_PATH)))
    sensor_data = sio.loadmat(open("{0}/Phi/sensor_fit.mat".format(DATA_PATH)))
    lsqr = np.squeeze(np.asarray(sensor_data['lsqr_soln']))
    true_sensor_value = np.squeeze(np.asarray(sensor_data['true']))
    route = LineString([[point['lng'], point['lat']] for point in point_list], srid=4326)
    route.transform(900913)
    def build_point_dictionary(point):
      x,y = point.x, point.y
      point.set_srid(4326)
      point.transform(900913)
      return {
        'map': [x, y],
        'compare': point
      }
    sensors_transformed = [build_point_dictionary(p) for p in points]
    sensor_map = []
    for sensor_ind, sensor in enumerate(sensors_transformed):
      if sensor['compare'].distance(route) < FUZZY_DIST:
          sensor_map.append({
              'loc':sensor['map'],
              'true':true_sensor_value[sensor_ind],
              'predicted':lsqr[sensor_ind]
          })
    return sensor_map

def plan(x1, y1, x2, y2):
  url = 'http://maps.googleapis.com/maps/api/directions/json?origin=%s,%s&destination=%s,%s&sensor=false&alternatives=true'
  r = requests.get(url % (x1, y1, x2, y2))
  json = r.json()
  routes = json['routes']
  points = pickle.load(open("{0}/Phi/sensors.pickle".format(DATA_PATH)))
  sensor_data = sio.loadmat(open("{0}/Phi/sensor_fit.mat".format(DATA_PATH)))
  lsqr = np.squeeze(np.asarray(sensor_data['lsqr_soln']))
  true_sensor_value = np.squeeze(np.asarray(sensor_data['true']))
  sensor_map = []
  def build_point_dictionary(point):
    x,y = point.x, point.y
    point.set_srid(4326)
    point.transform(900913)
    return {
      'map': [x, y],
      'compare': point
    }
  sensors_transformed = [build_point_dictionary(p) for p in points]
  for route_index, route in enumerate(routes):
    ls = decode_line(route['overview_polyline']['points'])
    ls.set_srid(4326)
    ls_4326 = ls.clone()
    ls.transform(900913)
    for sensor_ind, sensor in enumerate(sensors_transformed):
      if sensor['compare'].distance(ls) < FUZZY_DIST:
          sensor_map.append({
              'loc':sensor['map'],
              'true':true_sensor_value[sensor_ind],
              'predicted':lsqr[sensor_ind]
          })

  return [json, sensor_map]

def decode_line(encoded):
    """Decodes a polyline that was encoded using the Google Maps method.
    See http://code.google.com/apis/maps/documentation/polylinealgorithm.html
    
    This is a straightforward Python port of Mark McClure's JavaScript polyline decoder
    (http://facstaff.unca.edu/mcmcclur/GoogleMaps/EncodePolyline/decode.js)
    and Peter Chng's PHP polyline decode
    (http://unitstep.net/blog/2008/08/02/decoding-google-maps-encoded-polylines-using-php/)
    """
    encoded_len = len(encoded)
    index = 0
    array = []
    lat = 0
    lng = 0
    while index < encoded_len:
        b = 0
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng
        array.append(Point(lng * 1e-5, lat * 1e-5))
    return LineString(array)

def encode_line(line_string):
    """ Currently buggy, so just return the correctly ordered array that javascript doesn't even
    need to decode. This should be fixed at some point incase we have a better reason to encode lines.
    """
    encoded_string = ""
    point_so_far = (0, 0)
    for point in line_string:
        lng = point[0]
        lat = point[1]
        lat = int_value = int(round(lat * 100000, 0))
        lng = int_value = int(round(lng * 100000, 0))
        long_encode = encode_lat_or_long(lng - point_so_far[0])
        lat_encode = encode_lat_or_long(lat - point_so_far[1])
        point_so_far = (lng, lat)
        encoded_string += lat_encode + long_encode
    return [[pt[1], pt[0]] for pt in line_string]
    #return encoded_string

def encode_lat_or_long(int_value):
    encoding_string = ""
    if int_value < 0:
        int_value = ~(int_value << 1)
    else:
        int_value = (int_value << 1)
    while int_value:
        bottom_five = int_value & 0x01f
        int_value = int_value >> 5
        if int_value > 0:
            bottom_five = bottom_five | 0x020
        bottom_five += 63
        encoding_string += str(unichr(bottom_five))
    return encoding_string

# This seems important. Why undefined?
def undefined():
  import csv
  from django.contrib.gis.geos import Point, LineString
  import pickle

  points = []
  for row in csv.DictReader(open("{0}/Phi/sensors.csv".format(DATA_PATH))):
    p = Point(float(row['Longitude']), float(row['Latitude']))
    points.append(p)

  pickle.dump(points, open("{0}/Phi/sensors.pickle".format(DATA_PATH), 'w'))
