__author__ = 'lei'
from phidata.models import Route
from django.db import connection
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from cStringIO import StringIO
import phidata.config as config
from collections import defaultdict
class E2Routes:
    def clear(self):
        Route.objects.all().delete()
        return self
    @staticmethod
    def _array_to_postgres(xs):
        return '{' + ','.join(map(str, xs)) + '}'

    def load(self):
        sql_query = '''select links from experiment2_routes where od_route_index < 50;'''
        cursor = connection.cursor()
        cursor.execute(sql_query)

        sio = StringIO()
        for id, (links, ) in enumerate(cursor):
            sio.write('\t'.join([str(id), E2Routes._array_to_postgres(links)]))
            sio.write('\n')

        sio.reset()
        cursor.copy_from(sio, 'phidata_route')
        return self


if __name__ == "__main__":
    E2Routes().clear().load()
