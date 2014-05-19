import os
import pico
import requests
import pickle
import scipy.io as sio
import numpy as np
import json
from collections import defaultdict
from django.contrib.gis.geos import Point, LineString

DATA_PATH = '/home/ubuntu/datasets'
FUZZY_DIST = 10
NUM_WORST_ROUTES = 10

sensor_data = sio.loadmat(open("{0}/Phi/sensor_fit.mat".format(DATA_PATH)))
lsqr = np.squeeze(np.asarray(sensor_data['lsqr_soln']))
true_sensor_value = np.squeeze(np.asarray(sensor_data['true']))

back_map = pickle.load(open("{0}/Phi/od_back_map.pickle".format(DATA_PATH)))
condensed_map = defaultdict(list)
for k, v in back_map.iteritems():
    condensed_map[v].append(k)

route_split = sio.loadmat(open("{0}/Phi/outputSmallData.mat".format(DATA_PATH)))
route_split['x'] = np.squeeze(np.asarray(route_split['xLBFGS']))
route_split['x_true'] = np.squeeze(np.asarray(route_split['x_true']))

lookup = pickle.load(open("{0}/Phi/lookup.pickle".format(DATA_PATH)))
rlookup = {}
for index in lookup:
  rlookup[lookup[index]] = index

points = pickle.load(open("{0}/Phi/sensors.pickle".format(DATA_PATH)))

def build_point_dictionary(point):
  x,y = point.x, point.y
  point.set_srid(4326)
  point.transform(900913)
  return {
    'map': [x, y],
    'compare': point
  }
sensors_transformed = [build_point_dictionary(p) for p in points]

def sensors(point_list):
    route = LineString([[point['lng'], point['lat']] for point in point_list], srid=4326)
    route.transform(900913)
    sensor_map = []
    for sensor_ind, sensor in enumerate(sensors_transformed):
      if sensor['compare'].distance(route) < FUZZY_DIST:
          sensor_map.append({
              'loc':sensor['map'],
              'true':true_sensor_value[sensor_ind],
              'predicted':lsqr[sensor_ind]
          })
    return sensor_map

def plan(x1, y1, x2, y2, o, d):
  o = rlookup[float(o)]
  d = rlookup[float(d)]
  #url = 'http://maps.googleapis.com/maps/api/directions/json?origin=%s,%s&destination=%s,%s&sensor=false&alternatives=true'
  #r = requests.get(url % (x1, y1, x2, y2))
  #json_ = r.json()
  json_ = json.load(open('{0}/Phi/data/%s_%s.json'.format(DATA_PATH) % (o, d)))
  routes = json_['routes']
  sensor_map = []
  for route_index, route in enumerate(routes):
    if (o, d) in condensed_map:
        predicted_split = route_split['x'][condensed_map[(o, d)][route_index]]
        true_split = route_split['x_true'][condensed_map[(o, d)][route_index]]
        json_['routes'][route_index]['predicted_split'] = predicted_split
        json_['routes'][route_index]['true_split'] = true_split
        json_['routes'][route_index]['split_error'] = predicted_split - true_split
    else:
        json_['routes'][route_index]['split_error'] = 'black'
        json_['routes'][route_index]['predicted_split'] = 'OD pair omitted from calculation'
        json_['routes'][route_index]['true_split'] = 'OD pair omitted from calculation'
    json_['routes'][route_index]['num_sensors'] = 0
    ls = decode_line(route['overview_polyline']['points'])
    ls.set_srid(4326)
    ls_4326 = ls.clone()
    ls.transform(900913)
    for sensor_ind, sensor in enumerate(sensors_transformed):
      if sensor['compare'].distance(ls) < FUZZY_DIST:
          json_['routes'][route_index]['num_sensors'] += 1
          sensor_map.append({
              'loc':sensor['map'],
              'true':true_sensor_value[sensor_ind],
              'predicted':lsqr[sensor_ind]
          })

  return [json_, sensor_map]

def get_worst_routes():
    diff = route_split['x'] - route_split['x_true']
    worst_routes, indices = thresholder(diff, NUM_WORST_ROUTES)
    json_ = {'routes': {}}
    for idx in indices:
        o, d = back_map[idx]
        od_pair_json = json.load(open('{0}/Phi/data/%s_%s.json'.format(DATA_PATH) % (o, d)))
        routes = od_pair_json['routes']
        sensor_map = []
        for route_index, route in enumerate(routes):
            if condensed_map[(o, d)][route_index] != idx:
                continue
            predicted_split = route_split['x'][idx]
            true_split = route_split['x_true'][idx]
            json_['routes'][idx] = route
            json_['routes'][idx]['predicted_split'] = predicted_split
            json_['routes'][idx]['true_split'] = true_split
            json_['routes'][idx]['split_error'] = predicted_split - true_split
            ls = decode_line(route['overview_polyline']['points'])
            ls.set_srid(4326)
            ls.transform(900913)
            json_['routes'][idx]['num_sensors'] = 0
            for sensor_ind, sensor in enumerate(sensors_transformed):
              if sensor['compare'].distance(ls) < FUZZY_DIST:
                json_['routes'][idx]['num_sensors'] += 1

    json_['routes'] = [v for k, v in json_['routes'].iteritems()]
    return json_

def thresholder(y,m):
    ys_idx = np.argsort(-np.abs(y))
    support_idx = ys_idx[:m]

    y_thresh = np.zeros(y.size)
    y_thresh[support_idx] = y[support_idx]

    thresh = y[ys_idx[m]] if m < y.size else 0 # smallest zeroed value
    return y_thresh, support_idx

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
