# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'WorldBorder'
        db.create_table(u'orm_worldborder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('area', self.gf('django.db.models.fields.IntegerField')()),
            ('pop2005', self.gf('django.db.models.fields.IntegerField')()),
            ('fips', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('iso2', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('iso3', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('un', self.gf('django.db.models.fields.IntegerField')()),
            ('region', self.gf('django.db.models.fields.IntegerField')()),
            ('subregion', self.gf('django.db.models.fields.IntegerField')()),
            ('lon', self.gf('django.db.models.fields.FloatField')()),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('mpoly', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal(u'orm', ['WorldBorder'])

        # Adding model 'Sensor'
        db.create_table(u'orm_sensor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pems_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('freeway', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('district_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('county_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('city_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('state_pm', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('absolute_pm', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=900913)),
            ('sensor_length', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('sensor_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('lanes', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('user_id_1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('user_id_2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('user_id_3', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('user_id_4', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('shape_length', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('shape_area', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('cnty', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('taz_id', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('pop_20', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('hh_20', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('emp_20', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('pop_35', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('hh_35', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('emp_35', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('cnty_1', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('taz_id_1', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('pop_08', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('hh_08', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('emp_08', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'orm', ['Sensor'])


    def backwards(self, orm):
        # Deleting model 'WorldBorder'
        db.delete_table(u'orm_worldborder')

        # Deleting model 'Sensor'
        db.delete_table(u'orm_sensor')


    models = {
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
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '900913'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'pems_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pop_08': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pop_20': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'pop_35': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
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
        u'orm.worldborder': {
            'Meta': {'object_name': 'WorldBorder'},
            'area': ('django.db.models.fields.IntegerField', [], {}),
            'fips': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso2': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'iso3': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lon': ('django.db.models.fields.FloatField', [], {}),
            'mpoly': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pop2005': ('django.db.models.fields.IntegerField', [], {}),
            'region': ('django.db.models.fields.IntegerField', [], {}),
            'subregion': ('django.db.models.fields.IntegerField', [], {}),
            'un': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['orm']