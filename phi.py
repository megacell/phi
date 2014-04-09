import os
from lib import google_lines
import pickle
import random
from django.contrib.gis.geos import Point, LineString
import json
from lib.console_progress import ConsoleProgress

data_prefix = 'data'
N_TAZ = 321
N_TAZ_TARGET = 75
FUZZY_DIST = 10

def route_sensors(route):
  intersects = []
  for i, s in enumerate(sensors):
    if s.distance(route) < FUZZY_DIST:
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
sensors = []
for i, p in enumerate(points):
  p.set_srid(4326)
  p.transform(900913)
  sensors.append(p)

lookup = pickle.load(open(data_prefix+'/lookup.pickle'))
files = os.listdir(data_prefix+'/data')

selected_origins = random.sample(xrange(N_TAZ), N_TAZ_TARGET)
ll = [lookup[o] for o in selected_origins]
print ll

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
  
gen_tt = ConsoleProgress(N_TAZ_TARGET, message="Computing Phi")
out = open(data_prefix+'/routes_condensed.csv', 'w')
out.write('id#corigin#cdestination#origin#destination#route#origin_taz#destination_taz#route#sensors\n')
count = 0
for index_o, o in enumerate(origins):
  for index_d, d in enumerate(origins[o]):
    for i, route in enumerate(getRoutes(o, d)):
      rs = route_sensors(route)
      out.write('%s#%s#%s#%s#%s#%s#%s#%s#%s#%s\n' % (count, index_o, index_d, o, d, i, lookup[o], lookup[d], route, str(rs)))
      origins[o][d].append(rs)
  gen_tt.update_progress(index_o)
out.close()
gen_tt.finish()

pickle.dump(origins, open(data_prefix+'/phi_condensed.pickle', 'w'))
