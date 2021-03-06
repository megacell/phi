from django.contrib.gis.db import models
import django_utils.config as config

class Sensor(models.Model):
    pems_id = models.IntegerField(null=True, blank=True)
    freeway = models.CharField(null=True, blank=True, max_length=50)
    direction = models.CharField(null=True, blank=True, max_length=2) # N, S, E, W
    district_id = models.IntegerField(null=True, blank=True)
    county_id = models.IntegerField(null=True, blank=True)
    city_id = models.IntegerField(null=True, blank=True)
    state_pm = models.CharField(null=True, blank=True, max_length=50)
    absolute_pm = models.FloatField(null=True, blank=True)

    location = models.PointField(srid=config.canonical_projection)
    location_dist = models.PointField(srid=config.google_projection, null=True, blank=True)
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

    # whether or not the sensor is positioned on a highway or arterial roadway
    road_type = models.CharField(null=True, blank=True, max_length=50, default='Freeway')

    def location_wgs84(self):
        return self.location_dist

    # Returns the string representation of the model.
    def __unicode__(self):
        return "%s %s" % (self.name, repr(self.location_wgs84().coords))

class MatrixTaz(models.Model):
    matrix_id = models.IntegerField()
    taz_id = models.FloatField(db_index=True)

class ExperimentRoute(models.Model):
    route = models.ForeignKey('Route')
    vector_index = models.IntegerField()
    value = models.FloatField(null=True, blank=True)
    description = models.TextField()
    true_split = models.BooleanField(default=False)

    class Meta:
        index_together = (("vector_index", "description"),)

class Experiment(models.Model):
    description = models.TextField()
    name = models.TextField()
    run_time = models.DateTimeField()

class ExperimentSensor(models.Model):
    experiment = models.ForeignKey('Experiment')
    sensor = models.ForeignKey('Sensor')
    vector_index = models.IntegerField()
    value = models.FloatField(null=True, blank=True)

class Origin(models.Model):
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    cnty = models.FloatField()
    taz_id = models.FloatField()
    pop20 = models.FloatField()
    hh20 = models.FloatField()
    emp20 = models.FloatField()
    pop35 = models.FloatField()
    hh35 = models.FloatField()
    emp35 = models.FloatField()
    cnty_1 = models.FloatField()
    taz_id_1 = models.FloatField()
    pop08 = models.FloatField()
    hh08 = models.FloatField()
    emp08 = models.FloatField()
    geom = models.PolygonField(srid=config.canonical_projection)
    geom_dist = models.PolygonField(srid=config.google_projection, null=True, blank=True)
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return "TAZ: %s, Centroid: %s" % (self.taz_id, repr(self.geom.centroid.coords))

# Auto-generated `LayerMapping` dictionary for Origin model
origin_mapping = {
    'shape_leng' : 'Shape_Leng',
    'shape_area' : 'Shape_Area',
    'cnty' : 'CNTY',
    'taz_id' : 'TAZ_ID',
    'pop20' : 'POP20',
    'hh20' : 'HH20',
    'emp20' : 'EMP20',
    'pop35' : 'POP35',
    'hh35' : 'HH35',
    'emp35' : 'EMP35',
    'cnty_1' : 'CNTY_1',
    'taz_id_1' : 'TAZ_ID_1',
    'pop08' : 'POP08',
    'hh08' : 'HH08',
    'emp08' : 'EMP08',
    'geom' : 'POLYGON',
}

class Waypoint(models.Model):
    """
    geom is voronoi parition, location is center (location of tower)
    """
    category = models.CharField(null=True, blank=True, max_length=100)
    geom = models.PolygonField(srid=config.canonical_projection, null=True, blank=True)
    geom_dist = models.PolygonField(srid=config.google_projection, null=True, blank=True)
    location = models.PointField(srid=config.canonical_projection)
    location_dist = models.PointField(srid=config.google_projection, null=True, blank=True)
    density_id = models.IntegerField()

    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return "Category: %s, Center: %s" % (self.category, repr(self.location.coords))

class Route(models.Model):
    geom = models.LineStringField(srid=config.canonical_projection)
    geom_dist = models.LineStringField(srid=config.google_projection, null=True, blank=True)
    summary = models.CharField(max_length=100)
    origin_taz = models.FloatField()
    destination_taz = models.FloatField()
    od_route_index = models.IntegerField()
    travel_time = models.FloatField(null=True, blank=True) #can always recover from JSON
    json_contents = models.TextField()

    objects = models.GeoManager()

    class Meta:
        unique_together = (("origin_taz", "destination_taz", "od_route_index"),)
        index_together = (("origin_taz", "destination_taz"),)

    # Returns the string representation of the model.
    def __unicode__(self):
        return "OD: %s to %s, Travel Time: %s Centroid: %s" % (self.origin_taz, self.destination_taz, self.travel_time or 0, repr(self.geom.centroid.coords))

class Experiment2Route(models.Model):
    geom = models.MultiLineStringField(srid=config.canonical_projection)
    geom_dist = models.MultiLineStringField(srid=config.google_projection, null=True, blank=True)

    start_point = models.PointField(srid=config.canonical_projection)
    end_point = models.PointField(srid=config.canonical_projection)

    origin_taz = models.FloatField()
    destination_taz = models.FloatField()
    od_route_index = models.IntegerField()

    # this is the total number of trajectories collapsed onto this single route
    flow_count = models.IntegerField()

    objects = models.GeoManager()

    class Meta:
        unique_together = (("origin_taz", "destination_taz", "od_route_index"),)
        index_together = (("origin_taz", "destination_taz"),)
