import os
import pico
import requests
import pickle
from django.contrib.gis.geos import Point, LineString

DATA_PATH = '/home/steve/megacell/datasets'
FUZZY_DIST = 10

def plan(x1, y1, x2, y2):
  url = 'http://maps.googleapis.com/maps/api/directions/json?origin=%s,%s&destination=%s,%s&sensor=false&alternatives=true'
  r = requests.get(url % (x1, y1, x2, y2))
  json = r.json()
  routes = json['routes']
  points = pickle.load(open("{0}/Phi/sensors.pickle".format(DATA_PATH)))
  sensor_map = []
  def build_point_dictionary(point):
    x,y = point.x, point.y
    point.set_srid(4326)
    point.transform(900913)
    return {
      'map': [x, y],
      'compare': point
    }
  ls_set = []
  sensors_transformed = [build_point_dictionary(p) for p in points]
  for route_index, route in enumerate(routes):
    ls = decode_line(route['overview_polyline']['points'])
    ls.set_srid(4326)
    ls_4326 = ls.clone()
    ls.transform(900913)
    for sensor in sensors_transformed:
      if sensor['compare'].distance(ls) < FUZZY_DIST:
        sensor_map.append(sensor['map'])

    for route_b_index, route_b in enumerate(routes):
        if route_b_index > route_index:
            ls_b = decode_line(route_b['overview_polyline']['points'])
            ls_b.set_srid(4326)
            ls_set = find_shared_segments(ls_4326, ls_b.clone())
            break
            #TODO: this needs to iterate through both routes appropriately, going until a deviation from
            # both before ending the polyline and moving on to the next one
            route_similarity_points = []
            ls_b.transform(900913)
            for pt in ls:
                place = Point(pt)
                place.set_srid(4326)
                place.transform(900913)
                dist = place.distance(ls_b)
                if dist < FUZZY_DIST:
                    place = Point(pt)
                    place.set_srid(4326)
                    route_similarity_points.append(place)
                else:
                    if len(route_similarity_points) > 1:
                        ls_set.append(encode_line(LineString(route_similarity_points)))
                        route_similarity_points = []
            if len(route_similarity_points) > 1:
                ls_set.append(encode_line(LineString(route_similarity_points)))
  return [json, sensor_map, ls_set]

def condense_to_same_route(R, S):
    """Preprocess to create routes with all shared points on each route
    Keyword arguments:
    route_a -- LineString route
    route_b -- LineString route
    This method should be commutative.
    """
    S_trans = S.clone()
    S_trans.set_srid(4326)
    S_trans.transform(900913)
    R_trans = R.clone()
    R_trans.set_srid(4326)
    R_trans.transform(900913)
    # Add R points to S
    R_in_S = []
    for pair in R:
        pt = Point(pair, srid=4326)
        pt.transform(900913)
        dist = pt.distance(S_trans)
        if dist > FUZZY_DIST:
            continue
        S_len = len(S_trans)
        for index, S_start in enumerate(S_trans):
            if index == S_len - 1:
                break
            S_end = S_trans[index + 1]
            s_line = LineString([S_start, S_end])
            s_line_dist = pt.distance(s_line)
# TODO: should this be fuzzy equal?
            if s_line_dist == dist:
                R_in_S.append({'add_after':index,'value':pair})

def find_shared_segments(R, S):
  """Return a list of LineStrings where two routes overlap

  Keyword arguments:
  route_a -- LineString route
  route_b -- LineString route
  This method should be commutative.
  
  Algorithmic idea:
  For a given set of routes that are not identical:
    - Go through each route (R and S), and make a list, P(*) for each that contains points not on the other
      route.
    - Starting with P(R), iterate through elements p_i = P(R)_i:
      - Find p_i in original polyline, R.
      - Find the vertex of the item before p_i in R, v_s. v_s should be on the other route S.
      - Starting from this element in R, move forward through route until you find the first vertex
        that is on S, call this v_f. Remove elements not on S from P(R), including p_i
      - Starting from v_s, find closest vertex on S, call it g. This could be before or after where v_s
        intersects the route.
      - Move along S in both directions from g, taking ordered pairs where order is index in S, and identify
        the first pair where the first element is on R, but the second element is not.
        - If the first element of this tuple is after g, then that element is end of a shared leg.
        - Otherwise, v_s is the end of that shared leg.
      - Starting from v_f, find closest vertex on S, call it g, this could be before or after where v_f
        intersects the route.
      - Move along S in both directions from g, taking ordered pairs where order is index in S, and identify
        the first pair where the first element is not on R, but the second element is.
        - If the second element of this tuple is before g, then that element is the start of a shared leg.
        - Otherwise, v_f is the start of that shared leg.
    - At this point, we have a list of starting points and ending points of shared legs, combining them
      in to a polyline from the two routes seems tractable. TODO: figure this out when brain is less fried.
  """
  R_points_not_on_S = []
  S_points_not_on_R = []
  S_trans = S.clone()
  S_trans.set_srid(4326)
  S_trans.transform(900913)
  for pt in R:
      place = Point(pt)
      place.set_srid(4326)
      place.transform(900913)
      if place.distance(S_trans) > FUZZY_DIST:
          R_points_not_on_S.append(pt)
  #TODO: refactor these into single function call
  S_trans = S.clone()
  S_trans.set_srid(4326)
  S_trans.transform(900913)
  R_trans = R.clone()
  R_trans.set_srid(4326)
  R_trans.transform(900913)
  for pt in S:
      place = Point(pt, srid=4326)
      place.transform(900913)
      if place.distance(R_trans) > FUZZY_DIST:
          S_points_not_on_R.append(pt)
  # we know they start at the same point
  shared_leg_list = []
  shared_leg = []
  shared_leg_start_index = 0
  n = len(R_points_not_on_S)
  while n > 0:
      p_i = R_points_not_on_S[0]
      j = R.index(p_i)
      v_s = R[j - 1]
      f = j
      v_f = p_i
      while v_f in R_points_not_on_S:
          idx = R_points_not_on_S.index(v_f)
          del R_points_not_on_S[idx]
          n = n - 1
          f = f + 1
          v_f = R[f]
      # We know v_f is fuzzy-on S,  so we can iterate through pairs of S and find the segment it is fuzzy-on
      before_index = 0
      for i, start_vertex in enumerate(S):
          if i == len(S):
              break
          end_vertex = S[i + 1]
          line = LineString([start_vertex, end_vertex])
          line.set_srid(4326)
          line.transform(900913)
          pt = Point(v_s)
          pt.set_srid(4326)
          pt.transform(900913)
          if pt.distance(line) < FUZZY_DIST:
              before_index = i
              break
      # At this point, we know shared_leg_start_index..before_index is certainly on the path.
      shared_leg = S[shared_leg_start_index:(before_index+1)]
      shared_leg.append(v_s)
      after_index = before_index + 1
      # Either v_s is the end of the previous shared segment, or after_index or something following that,
      # so go until you find a point on S not on R, starting at after_index
      pt = Point(S[after_index], srid=4326)
      pt.transform(900913)
      while pt.distance(R_trans) < FUZZY_DIST:
          shared_leg.append(S[after_index])
          after_index = after_index + 1
      # should check that shared_leg is not just first element. In fact, TODO: go back an check what happens
      # if the first element is the only shared element.
      shared_leg_list.append(LineString(shared_leg))
      return shared_leg_list
      shared_leg = []
          # with this change i think shared leg is complete....
      # now we have to do the same thing, except with the end of the non-connected segment looking backwards

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

def undefined():
  import csv
  from django.contrib.gis.geos import Point, LineString
  import pickle

  points = []
  for row in csv.DictReader(open("{0}/Phi/sensors.csv".format(DATA_PATH))):
    p = Point(float(row['Longitude']), float(row['Latitude']))
    points.append(p)

  pickle.dump(points, open("{0}/Phi/sensors.pickle".format(DATA_PATH), 'w'))
