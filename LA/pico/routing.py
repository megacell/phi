import os
import pico
import requests
import pickle
from django.contrib.gis.geos import Point, LineString

DATA_PATH = '/home/steve/megacell/datasets'

def plan(x1, y1, x2, y2):
  url = 'http://maps.googleapis.com/maps/api/directions/json?origin=%s,%s&destination=%s,%s&sensor=false&alternatives=false'
  r = requests.get(url % (x1, y1, x2, y2))
  json = r.json()
  ls = decode_line(json['routes'][0]['overview_polyline']['points'])
  ls.set_srid(4326)
  ls.transform(900913)
  
  points = pickle.load(open("{0}/Phi/sensors.pickle".format(DATA_PATH)))
  sensors = []
  for p in points:
    x = p.x
    y = p.y
    p.set_srid(4326)
    p.transform(900913)
    if p.distance(ls) < 10:
      sensors.append([x, y])
  return [json, sensors]

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

def undefined():
  import csv
  from django.contrib.gis.geos import Point, LineString
  import pickle

  points = []
  for row in csv.DictReader(open("{0}/Phi/sensors.csv".format(DATA_PATH))):
    p = Point(float(row['Longitude']), float(row['Latitude']))
    points.append(p)

  pickle.dump(points, open("{0}/Phi/sensors.pickle".format(DATA_PATH), 'w'))
