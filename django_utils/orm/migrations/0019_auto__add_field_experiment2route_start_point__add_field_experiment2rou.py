# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Experiment2Route.start_point'
        db.add_column(u'orm_experiment2route', 'start_point',
                      self.gf('django.contrib.gis.db.models.fields.PointField')(default=None),
                      keep_default=False)

        # Adding field 'Experiment2Route.end_point'
        db.add_column(u'orm_experiment2route', 'end_point',
                      self.gf('django.contrib.gis.db.models.fields.PointField')(default=None),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Experiment2Route.start_point'
        db.delete_column(u'orm_experiment2route', 'start_point')

        # Deleting field 'Experiment2Route.end_point'
        db.delete_column(u'orm_experiment2route', 'end_point')


    models = {
        u'orm.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'run_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'orm.experiment2route': {
            'Meta': {'unique_together': "(('origin_taz', 'destination_taz', 'od_route_index'),)", 'object_name': 'Experiment2Route', 'index_together': "(('origin_taz', 'destination_taz'),)"},
            'destination_taz': ('django.db.models.fields.FloatField', [], {}),
            'end_point': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'flow_count': ('django.db.models.fields.IntegerField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {}),
            'geom_dist': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {'srid': '900913', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'od_route_index': ('django.db.models.fields.IntegerField', [], {}),
            'origin_taz': ('django.db.models.fields.FloatField', [], {}),
            'start_point': ('django.contrib.gis.db.models.fields.PointField', [], {})
        },
        u'orm.experimentroute': {
            'Meta': {'object_name': 'ExperimentRoute', 'index_together': "(('vector_index', 'description'),)"},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orm.Route']"}),
            'true_split': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'vector_index': ('django.db.models.fields.IntegerField', [], {})
        },
        u'orm.experimentsensor': {
            'Meta': {'object_name': 'ExperimentSensor'},
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orm.Experiment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orm.Sensor']"}),
            'value': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'vector_index': ('django.db.models.fields.IntegerField', [], {})
        },
        u'orm.matrixtaz': {
            'Meta': {'object_name': 'MatrixTaz'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matrix_id': ('django.db.models.fields.IntegerField', [], {}),
            'taz_id': ('django.db.models.fields.FloatField', [], {'db_index': 'True'})
        },
        u'orm.origin': {
            'Meta': {'object_name': 'Origin'},
            'cnty': ('django.db.models.fields.FloatField', [], {}),
            'cnty_1': ('django.db.models.fields.FloatField', [], {}),
            'emp08': ('django.db.models.fields.FloatField', [], {}),
            'emp20': ('django.db.models.fields.FloatField', [], {}),
            'emp35': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'geom_dist': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '900913', 'null': 'True', 'blank': 'True'}),
            'hh08': ('django.db.models.fields.FloatField', [], {}),
            'hh20': ('django.db.models.fields.FloatField', [], {}),
            'hh35': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pop08': ('django.db.models.fields.FloatField', [], {}),
            'pop20': ('django.db.models.fields.FloatField', [], {}),
            'pop35': ('django.db.models.fields.FloatField', [], {}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_leng': ('django.db.models.fields.FloatField', [], {}),
            'taz_id': ('django.db.models.fields.FloatField', [], {}),
            'taz_id_1': ('django.db.models.fields.FloatField', [], {})
        },
        u'orm.route': {
            'Meta': {'unique_together': "(('origin_taz', 'destination_taz', 'od_route_index'),)", 'object_name': 'Route', 'index_together': "(('origin_taz', 'destination_taz'),)"},
            'destination_taz': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            'geom_dist': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '900913', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json_contents': ('django.db.models.fields.TextField', [], {}),
            'od_route_index': ('django.db.models.fields.IntegerField', [], {}),
            'origin_taz': ('django.db.models.fields.FloatField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'travel_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'orm.sensor': {
            'Meta': {'object_name': 'Sensor'},
            'absolute_pm': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'city_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cnty': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'cnty_1': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'county_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'district_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'emp_08': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'emp_20': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'emp_35': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'freeway': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'hh_08': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hh_20': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'hh_35': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lanes': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'location_dist': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '900913', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'pems_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pop_08': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pop_20': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pop_35': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'road_type': ('django.db.models.fields.CharField', [], {'default': "'Freeway'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'sensor_length': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'sensor_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shape_area': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'shape_length': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'state_pm': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'taz_id': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'taz_id_1': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'user_id_1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_id_2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_id_3': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_id_4': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'orm.waypoint': {
            'Meta': {'object_name': 'Waypoint'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'geom_dist': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '900913', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'location_dist': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '900913', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['orm']