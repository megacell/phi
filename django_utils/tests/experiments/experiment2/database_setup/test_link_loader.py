from cStringIO import StringIO
from django.contrib.gis.geos import Point
import django_utils.config as config
from itertools import product
import shapefile
import unittest
from django_utils.experiments.experiment2.database_setup.link_loader import LinkLoader
from django.db import connection


class LinkData:
    def __init__(self):
        self.shp = StringIO()
        self.shx = StringIO()
        self.dbf = StringIO()
        self.wr = shapefile.Writer()

    @staticmethod
    def get_adjacent_points(x, y, max):
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if i == j:
                    continue
                if 0 <= x + i < max and 0 <= y+j < max:
                    yield x+i, y+j

    def get_links(self):
        # wgs84
        lat = [
            33.974394,
            33.974465,
            33.974465,
            33.974572,
            33.981862,
            33.982146,
            33.982075,
            33.982075,
            33.988979,
            33.988836,
            33.988907,
            33.988694,
            33.996806,
            33.996664,
            33.996735,
            33.996806]

        long = [
            -118.308914,
            -118.300266,
            -118.291554,
            -118.281169,
            -118.309107,
            -118.300266,
            -118.291168,
            -118.28104,
            -118.309021,
            -118.300266,
            -118.291426,
            -118.280783,
            -118.308935,
            -118.300095,
            -118.291855,
            -118.280525]

        links = []

        for i, j in product(range(len(lat)), range(len(lat))):
            for k, l in LinkData.get_adjacent_points(i,j,4):
                links.append([LinkData.transform(long[i], lat[j]), LinkData.transform(long[k], lat[l])])

        return links

    @staticmethod
    def transform(long, lat):
        p = Point(long, lat)
        p.srid=config.canonical_projection
        print p.ewkt
        p.transform(config.EPSG32611)
        return (p.x, p.y)

    def make_shapefile(self):
        self.wr.field()
        for id, l in enumerate(self.get_links()):
            print l
            self.wr.line([l])
            self.wr.record([id, 1, 2, 3, 4, 5, 6, -id])

        self.wr.saveShp(self.shp)
        self.wr.saveShx(self.shx)
        self.wr.saveDbf(self.dbf)

        self.shp.reset()
        self.shx.reset()
        self.dbf.reset()

        return self.shp, self.shx, self.dbf

class LinkLoaderTest(unittest.TestCase):
    def test_link_loading(self):
        ld = LinkData()
        shp, shx, dbf = ld.make_shapefile()
        reader = shapefile.Reader(shp=shp, shx=shx, dbf=dbf)
        ll = LinkLoader(connection, reader)

        ll.load()
