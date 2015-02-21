__author__ = 'lei'
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
import models
#from rest_framework_gis import serializers as gis_serializers

class LinkSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = models.Link
        geo_field = 'geom'
        fields = ('id', 'geom')

class LinkFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LinkFlow
        fields = ('link_id', 'flow', 'flow_type')

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Route
        fields = ('id', 'links')

class CellSerializer(gis_serializers.GeoFeatureModelSerializer):
    class Meta:
        model = models.Cell
        geo_field = 'geom'
        fields = ('id', 'geom', 'location')

class LinkTableSerializer(serializers.Serializer):
    links = serializers.ListField(child=serializers.IntegerField())
    link_id = serializers.IntegerField()
