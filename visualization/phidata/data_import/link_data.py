__author__ = 'lei'
from phidata.models import Link, LinkFlow
from django.db import connection
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from cStringIO import StringIO
import phidata.config as config
from collections import defaultdict
class PhiLinks:
    def clear(self):
        Link.objects.all().delete()
        return self

    def load(self):
        sql_query = '''select link_id, geom from link_geometry;'''
        cursor = connection.cursor()
        cursor.execute(sql_query)

        sio = StringIO()
        for id, geom in cursor:
            mls = MultiLineString(GEOSGeometry(geom))
            mls.set_srid(config.EPSG4326)

            sio.write('\t'.join([str(id), mls.ewkt]))
            sio.write('\n')

        sio.reset()
        cursor.copy_from(sio, 'phidata_link')
        return self

class TrueFlows:
    def __init__(self):
        self.flow_type = "true_flow"

    def clear(self):
        LinkFlow.objects.all().delete()
        return self

    def load(self):
        sql_query = '''select link_ids from experiment2_trajectories where commute_direction=1;'''
        cursor = connection.cursor()
        cursor.execute(sql_query)

        linkcounts = defaultdict(lambda: 0)
        for (link_ids, ) in cursor:
            for id in link_ids:
                linkcounts[id] += 1

        sio = StringIO()
        for id in linkcounts.keys():
            sio.write('\t'.join([str(id), str(linkcounts[id]), self.flow_type, str(id)]))
            sio.write('\n')
        sio.reset()

        cursor.copy_from(sio, 'phidata_linkflow')
        return self

if __name__ == "__main__":
    PhiLinks().clear().load()
    TrueFlows().clear().load()
