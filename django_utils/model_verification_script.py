import django.contrib.gis.db.models.query
from orm.models import *
a = WorldBorder.objects.all()
b = Sensor.objects.all()

assert isinstance(a, (django.contrib.gis.db.models.query.GeoQuerySet)), "Not a QuerySet, but a %s" % type(a)
assert isinstance(b, (django.contrib.gis.db.models.query.GeoQuerySet)), "Not a QuerySet, but a %s" % type(b)
print "Tests passed."
