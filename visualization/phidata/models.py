from django.contrib.gis.db import models
import config

# Remove with Django 1.8 release, which will have postgres package with an ArrayField
from djorm_pgarray.fields import ArrayField
from djorm_expressions.models import ExpressionManager

#from django.contrib.postgres.fields import ArrayField
# Create your models here.

# Map links
class Link(models.Model):
    id = models.IntegerField(primary_key=True)

    # id from the OSM map
    #orig_id = models.IntegerField()

    geom = models.MultiLineStringField(srid=config.EPSG4326)


# Link flow
class LinkFlow(models.Model):
    link_id = models.ForeignKey('Link')

    flow = models.FloatField()

    # Type of flow
    flow_type = models.CharField(max_length=255)

class Route(models.Model):
    id = models.IntegerField(primary_key=True)
    links = ArrayField(dbtype="int")

class TAZ(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = models.PolygonField(srid=config.EPSG4326)

class Cell(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = models.PolygonField(srid=config.EPSG4326)
    location = models.PointField(srid=config.EPSG4326)

class CellRouteMap(models.Model):
    id = models.IntegerField(primary_key=True)
    routes = ArrayField(dbtype="int")

class LinkTable:
    def __init__(self, link_id, links):
        self.link_id = link_id

        self.links = list(links)
