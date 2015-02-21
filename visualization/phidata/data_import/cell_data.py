__author__ = 'lei'
from phidata.models import Cell, CellRouteMap, Route
from django.db import connection
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from cStringIO import StringIO
import phidata.config as config
from collections import defaultdict
class CellTowers:
    def clear(self):
        Cell.objects.all().delete()
        return self

    @staticmethod
    def _array_to_postgres(xs):
        return '{' + ','.join(map(str, xs)) + '}'

    def load(self, density):
        sql_query = '''select id, ST_AsEWKT(geom), ST_AsEWKT(location) from orm_waypoint where density_id = %s;'''
        cursor = connection.cursor()
        cursor.execute(sql_query, [density])

        sio = StringIO()
        for id, geom, location in cursor:
            if geom is None:
                continue
            print geom
            sio.write('\t'.join([str(id), geom, location]))
            sio.write('\n')

        sio.reset()
        cursor.copy_from(sio, 'phidata_cell')
        return self

class CellRouteMapGenerator:
    def clear(self):
        CellRouteMap.objects.all().delete()
        return self

    @staticmethod
    def _array_to_postgres(xs):
        return '{' + ','.join(map(str, xs)) + '}'

    def load(self):
        sql_query = '''select c.id as id, array_agg(l.id) as links from phidata_cell c, phidata_link l where ST_Intersects(c.geom, l.geom) group by c.id;'''
        cursor = connection.cursor()
        cursor.execute(sql_query)
        celltolinkmap = dict()
        for id, links in cursor:
            celltolinkmap[id] = links
        linktoroutemap = defaultdict(set)
        for r in Route.objects.all():
            for l in r.links:
                linktoroutemap[l].add(r.id)
        celltoroutemap = defaultdict(set)
        for c in celltolinkmap.keys():
            for l in celltolinkmap[c]:
                celltoroutemap[c].update(linktoroutemap[l])
        sio = StringIO()

        for c in celltoroutemap:
            sio.write('\t'.join([str(c), CellRouteMapGenerator._array_to_postgres(celltoroutemap[c])]))
            sio.write('\n')
        sio.reset()
        cursor.copy_from(sio, 'phidata_cellroutemap')


if __name__ == "__main__":
    CellTowers().clear().load(1000)
    CellRouteMapGenerator().clear().load()
