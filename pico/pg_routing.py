import pico
import psycopg2
from psycopg2.extras import DictCursor
from django.contrib.gis.geos import GEOSGeometry

dbname = 'los_angeles'
conn_string = "host='localhost' dbname='%s' user='postgres'" % (dbname)
conn = psycopg2.connect(conn_string)

def ksp(x1, y1, x2, y2):
  cursor = conn.cursor(cursor_factory=DictCursor)
  
  cursor.execute("""
    SELECT source
    FROM ways
    ORDER BY st_distance(the_geom, st_setsrid(st_makepoint(%s, %s), 4326))
    LIMIT 1
  """, (y1, x1))
  start = cursor.fetchone()[0]

  cursor.execute("""
    SELECT target
    FROM ways
    ORDER BY st_distance(the_geom, st_setsrid(st_makepoint(%s, %s), 4326))
    LIMIT 1
  """, (y2, x2))
  end = cursor.fetchone()[0]
  
  cursor.execute("""
    SELECT seq, id1 AS route, id2 AS node, id3 AS edge, cost
    FROM pgr_ksp(
      'SELECT gid as id, source, target, length as cost FROM ways',
       89568, 231932, 3, false);
  """)
  routes = cursor.fetchall()
  return routes

def match_step_way(x1, y1, x2, y2, color):
  cursor = conn.cursor(cursor_factory=DictCursor)
  cursor.execute("""
    SELECT st_asText(the_geom), (st_distance(st_transform(st_setsrid(st_makepoint(x1, y1), 4326), 900913), st_transform(st_setsrid(st_makepoint(%s, %s), 4326), 900913)) + 
    st_distance(st_transform(st_setsrid(st_makepoint(x2, y2), 4326), 900913), st_transform(st_setsrid(st_makepoint(%s, %s), 4326), 900913))) as distance
    FROM ways
    ORDER BY distance
    LIMIT 1
  """, (x1, y1, x2, y2))
  way1 = cursor.fetchone()
  
  cursor.execute("""
    SELECT st_asText(the_geom), (st_distance(st_transform(st_setsrid(st_makepoint(x2, y2), 4326), 900913), st_transform(st_setsrid(st_makepoint(%s, %s), 4326), 900913)) + 
    st_distance(st_transform(st_setsrid(st_makepoint(x1, y1), 4326), 900913), st_transform(st_setsrid(st_makepoint(%s, %s), 4326), 900913))) as distance
    FROM ways
    ORDER BY distance
    LIMIT 1
  """, (x1, y1, x2, y2))
  way2 = cursor.fetchone()
  
  if way1[1] < way2[1]: 
    ret = way1
  else:
    ret = way2
  
  return [map(lambda x: (x[1], x[0]), GEOSGeometry(ret[0]).coords), color]

def sp(start, end):
  cursor = conn.cursor(cursor_factory=DictCursor)
  cursor.execute("SELECT seq, id1 AS node, id2 AS edge, cost, b.the_geom as the_geom, b.gid as gid FROM pgr_dijkstra('\
    SELECT gid AS id,\
             source::integer,\
             target::integer,\
             length::double precision AS cost\
            FROM ways',\
    %s, %s, false, false) a LEFT JOIN ways b ON (a.id2 = b.gid);" % (start, end))
  geoms = []
  ids = []
  for way in cursor.fetchall():
    if('the_geom' in way and way['the_geom'] != None):
      geoms.append(map(lambda x: (x[1], x[0]), GEOSGeometry(way['the_geom']).coords))
      ids.append(way['gid'])
  return [geoms, ids]

def nearest_way(lon, lat):
  cursor = conn.cursor(cursor_factory=DictCursor)
  cursor.execute("""
    SELECT *, st_asText(the_geom) as text
    FROM ways
    ORDER BY st_distance(the_geom, st_setsrid(st_makepoint(%s, %s), 4326))
    LIMIT 1
  """, (lon, lat))
  nn = cursor.fetchone()
  return [nn, map(lambda x: (x[1], x[0]), GEOSGeometry(nn['text']).coords)]

