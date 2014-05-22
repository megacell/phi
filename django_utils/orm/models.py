from django.contrib.gis.db import models

class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField), and
    # overriding the default manager with a GeoManager instance.
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return self.name


class Sensor(models.Model):
    pems_id = models.IntegerField(null=True, blank=True)
    freeway = models.CharField(null=True, blank=True, max_length=50)
    direction = models.CharField(null=True, blank=True, max_length=2) # N, S, E, W
    district_id = models.IntegerField(null=True, blank=True)
    county_id = models.IntegerField(null=True, blank=True)
    city_id = models.IntegerField(null=True, blank=True)
    state_pm = models.CharField(null=True, blank=True, max_length=50)
    absolute_pm = models.FloatField(null=True, blank=True)

    location = models.PointField(srid=900913)
    objects = models.GeoManager()

    sensor_length = models.FloatField(null=True, blank=True)
    sensor_type = models.CharField(null=True, blank=True, max_length=50)
    lanes = models.IntegerField(null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=50)
    user_id_1 = models.IntegerField(null=True, blank=True)
    user_id_2 = models.IntegerField(null=True, blank=True)
    user_id_3 = models.IntegerField(null=True, blank=True)
    user_id_4 = models.IntegerField(null=True, blank=True)
    shape_length = models.FloatField(null=True, blank=True)
    shape_area = models.FloatField(null=True, blank=True)
    cnty = models.FloatField(null=True, blank=True)
    taz_id = models.FloatField(null=True, blank=True)
    pop_20 = models.FloatField(null=True, blank=True)
    hh_20 = models.FloatField(null=True, blank=True)
    emp_20 = models.FloatField(null=True, blank=True)
    pop_35 = models.FloatField(null=True, blank=True)
    hh_35 = models.FloatField(null=True, blank=True)
    emp_35 = models.FloatField(null=True, blank=True)
    cnty_1 = models.FloatField(null=True, blank=True)
    taz_id_1 = models.FloatField(null=True, blank=True)
    pop_08 = models.FloatField(null=True, blank=True)
    hh_08 = models.FloatField(null=True, blank=True)
    emp_08 = models.FloatField(null=True, blank=True)

    def location_wgs84(self):
        return self.location.transform(4326, clone=True)

    # Returns the string representation of the model.
    def __unicode__(self):
        return "%s %s" % (self.name, repr(self.location_wgs84().coords))
