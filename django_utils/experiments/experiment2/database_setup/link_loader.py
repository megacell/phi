from django.contrib.gis.geos import LineString
import shapefile
from django_utils import config as config
from django.db import connection
import cStringIO

class LinkLoader:

    def __init__(self, connection, shapefile_path):
        self.connection = connection
        self.shapefile_reader = shapefile.Reader(shapefile_path)

    def _read_geos(self):
        irecord = self.shapefile_reader.iterRecords()
        ishapes = self.shapefile_reader.iterShapes()

        # read entries into a dictionary which has ids mapped to geometries
        id_to_geometry = list()

        for i in range(self.shapefile_reader.numRecords):
            record = irecord.next()
            points = [tuple(x) for x in ishapes.next().points]

            id = int(record[0])

            line = LineString(points)
            line.set_srid(config.EPSG32611)

            defaultprojection = line.clone()
            defaultprojection.transform(config.canonical_projection)

            googleprojection = line.clone()
            googleprojection.transform(config.google_projection)

            id_to_geometry.append('\t'.join([str(i), str(id), defaultprojection.ewkt, googleprojection.ewkt, line.ewkt]))

        return '\n'.join(id_to_geometry)

    def load(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            DROP TABLE IF EXISTS link_geometry;
            CREATE TABLE link_geometry (
            link_index integer,
            link_id integer,
            geom geometry(LINESTRING, %s),
            geom_dist geometry(LINESTRING, %s),
            geom_orig geometry(LINESTRING, %s)
            );''',
            (config.canonical_projection,
            config.google_projection,
            config.EPSG32611)
        )

        sio = cStringIO.StringIO(self._read_geos())
        cursor.copy_from(sio, 'link_geometry')

def load_LA_links():
    global timeit, tic, lgl, toc
    import timeit

    tic = timeit.default_timer()
    lgl = LinkLoader(connection, config.DATA_DIR + '/LA_shps/links/LA_network_links_V2')
    lgl.load()
    toc = timeit.default_timer()
    print (toc - tic)

if __name__ == "__main__":
    load_LA_links()

