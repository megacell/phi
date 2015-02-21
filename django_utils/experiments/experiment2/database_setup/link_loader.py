from django_utils import config as config
from django.contrib.gis.geos import LineString
from django.db import connection

import cStringIO
import shapefile

class LinkLoader:

    def __init__(self, connection, sf):
        self.connection = connection
        if isinstance(sf, basestring):
            self.shapefile_reader = shapefile.Reader(sf)
        else:
            self.shapefile_reader = sf
        #print self.shapefile_reader.fields

    def _read_geos(self):
        '''
        Reads the geometries from the shapefile and dumps them into a string
        :returns:the id and geometries of the links in a string
        '''

        irecord = self.shapefile_reader.iterRecords()
        ishapes = self.shapefile_reader.iterShapes()

        # read entries into a dictionary which has ids mapped to geometries
        id_to_geometry = list()

        for i in range(self.shapefile_reader.numRecords):
            record = irecord.next()
            shape = ishapes.next()

            points = [tuple(x) for x in shape.points]

            id = int(record[0])
            orig_id = int(record[7])
            line = LineString(points)
            line.set_srid(config.EPSG32611)

            defaultprojection = line.clone()
            defaultprojection.transform(config.canonical_projection)

            googleprojection = line.clone()
            googleprojection.transform(config.google_projection)

            id_to_geometry.append('\t'.join([str(i), str(id), defaultprojection.ewkt, googleprojection.ewkt, line.ewkt, str(orig_id)]))

        return '\n'.join(id_to_geometry)

    def load(self):
        '''
        Loads the geometries from the shape file into the link_geometry table.
        This method will delete what ever is in the link_geometry and dependent tables and create a new one.
        :return:
        '''
        cursor = self.connection.cursor()
        cursor.execute('''
            DROP TABLE IF EXISTS link_geometry CASCADE;
            CREATE TABLE link_geometry (
            link_index integer,
            link_id integer,
            geom geometry(LINESTRING, %s),
            geom_dist geometry(LINESTRING, %s),
            geom_orig geometry(LINESTRING, %s),
            orig_id integer
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
    lg = LinkLoader(connection, config.DATA_DIR + '/LA_shps/links/LA_network_links_V2')
    lg.load()
