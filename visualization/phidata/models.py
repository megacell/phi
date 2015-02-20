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

