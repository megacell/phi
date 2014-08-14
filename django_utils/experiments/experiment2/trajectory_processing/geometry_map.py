from django.db import connection
from django.contrib.gis.geos import GEOSGeometry
class GeometryMap:
    geometry_map = None

    @staticmethod
    def map_origID_to_geometry():
        import timeit
        if GeometryMap.geometry_map == None:
            tic = timeit.default_timer()
            cursor = connection.cursor()
            cursor.execute('''
            SELECT link_id, geom, geom_dist, (geom_orig)
            FROM link_geometry;
            ''')
            GeometryMap.geometry_map = {id: GEOSGeometry(geom_orig) for id, _,_, geom_orig in cursor}
            toc = timeit.default_timer()
            print toc - tic
        return GeometryMap.geometry_map
