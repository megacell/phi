import os
from lib import google_lines
import pickle
import random
from django.contrib.gis.geos import Point, LineString
import json
import time
import numpy as np
from lib.console_progress import ConsoleProgress

data_prefix = 'data'
N_TAZ = 321
N_TAZ_TARGET = 321
N_RANDOM_SENSORS = 2000
FUZZY_DIST = 10
selected_origin_id = str(time.time())

used_sensors = set()

def route_sensors(route):
  intersects = []
  for i, s in enumerate(sensors):
    if s.distance(route) < FUZZY_DIST:
      used_sensors.add(i)
      intersects.append(i)
  return intersects

def getRoutes(o, d):
  routes = []
  data = json.load(open(data_prefix+'/data/%s_%s.json' % (o, d)))
  for route in data['routes']:
    gpolyline = route['overview_polyline']['points']
    linestring = google_lines.decode_line(gpolyline)
    linestring.set_srid(4326)
    linestring.transform(900913)
    routes.append(linestring)
  return routes

points = pickle.load(open(data_prefix+'/sensors.pickle'))
print points[0]
sensors = []
for i, p_ in enumerate(points):
  p_.set_srid(4326)
  p = p_.clone()
  p.transform(900913)
  sensors.append(p)

min_second_coord = 34.02343721919245
max_second_coord = 34.20876014972369
min_first_coord = -118.22269254921883
max_first_coord = -117.74684721230477

rand_first_coord = np.random.uniform(min_first_coord, max_first_coord, N_RANDOM_SENSORS)
rand_second_coord = np.random.uniform(min_second_coord, max_second_coord, N_RANDOM_SENSORS)
for i in xrange(N_RANDOM_SENSORS):
    p_ = Point(rand_first_coord[i], rand_second_coord[i])
    p_.set_srid(4326)
    p = p_.clone()
    points.append(p_)
    p.transform(900913)
    sensors.append(p)

pickle.dump(points, open(data_prefix+'/sensors_'+selected_origin_id+'.pickle', 'wb'))

lookup = pickle.load(open(data_prefix+'/lookup.pickle'))
files = os.listdir(data_prefix+'/data')

selected_origins = random.sample(xrange(N_TAZ), N_TAZ_TARGET)
ll = [lookup[o] for o in selected_origins]
print ll

metadata = {
  'id': selected_origin_id,
  'N_TAZ': N_TAZ,
  'N_TAZ_CONDENSED': N_TAZ_TARGET,
  'FUZZY_DIST': FUZZY_DIST
}

origins = {}
for file in files:
  file = file.replace('.json', '')
  o, d = map(int, file.split('_'))
  if o not in selected_origins or d not in selected_origins:
      continue
  if not o in origins:
    origins[o] = {}
  if not d in origins[o]:
    origins[o][d] = []
  
num_routes = 0

gen_tt = ConsoleProgress(N_TAZ_TARGET, message="Computing Phi")
out = open(data_prefix+'/routes_condensed'+selected_origin_id+'.csv', 'w')
out.write('id#corigin#cdestination#origin#destination#route#origin_taz#destination_taz#route#sensors\n')
count = 0
for index_o, o in enumerate(origins):
  for index_d, d in enumerate(origins[o]):
    routes = getRoutes(o, d)
    num_routes += len(routes)
    for i, route in enumerate(routes):
      rs = route_sensors(route)
      out.write('%s#%s#%s#%s#%s#%s#%s#%s#%s#%s\n' % (count, index_o, index_d, o, d, i, lookup[o], lookup[d], route, str(rs)))
      origins[o][d].append(rs)
  gen_tt.update_progress(index_o)
out.close()
gen_tt.finish()

metadata['N_ROUTES_CONDENSED'] = num_routes
metadata['N_SENSORS_USED'] = len(used_sensors)
print 'Sensors used:', metadata['N_SENSORS_USED']

pickle.dump(origins, open(data_prefix+'/phi_condensed'+selected_origin_id+'.pickle', 'w'))
pickle.dump(metadata, open(data_prefix+'/phi_metadata'+selected_origin_id+'.pickle', 'w'))
