# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('name', models.TextField()),
                ('run_time', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Experiment2Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
                ('geom_dist', django.contrib.gis.db.models.fields.MultiLineStringField(srid=3857, null=True, blank=True)),
                ('start_point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('end_point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('origin_taz', models.FloatField()),
                ('destination_taz', models.FloatField()),
                ('od_route_index', models.IntegerField()),
                ('flow_count', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentRoute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vector_index', models.IntegerField()),
                ('value', models.FloatField(null=True, blank=True)),
                ('description', models.TextField()),
                ('true_split', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentSensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vector_index', models.IntegerField()),
                ('value', models.FloatField(null=True, blank=True)),
                ('experiment', models.ForeignKey(to='orm.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MatrixTaz',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('matrix_id', models.IntegerField()),
                ('taz_id', models.FloatField(db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shape_leng', models.FloatField()),
                ('shape_area', models.FloatField()),
                ('cnty', models.FloatField()),
                ('taz_id', models.FloatField()),
                ('pop20', models.FloatField()),
                ('hh20', models.FloatField()),
                ('emp20', models.FloatField()),
                ('pop35', models.FloatField()),
                ('hh35', models.FloatField()),
                ('emp35', models.FloatField()),
                ('cnty_1', models.FloatField()),
                ('taz_id_1', models.FloatField()),
                ('pop08', models.FloatField()),
                ('hh08', models.FloatField()),
                ('emp08', models.FloatField()),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('geom_dist', django.contrib.gis.db.models.fields.PolygonField(srid=3857, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geom', django.contrib.gis.db.models.fields.LineStringField(srid=4326)),
                ('geom_dist', django.contrib.gis.db.models.fields.LineStringField(srid=3857, null=True, blank=True)),
                ('summary', models.CharField(max_length=100)),
                ('origin_taz', models.FloatField()),
                ('destination_taz', models.FloatField()),
                ('od_route_index', models.IntegerField()),
                ('travel_time', models.FloatField(null=True, blank=True)),
                ('json_contents', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pems_id', models.IntegerField(null=True, blank=True)),
                ('freeway', models.CharField(max_length=50, null=True, blank=True)),
                ('direction', models.CharField(max_length=2, null=True, blank=True)),
                ('district_id', models.IntegerField(null=True, blank=True)),
                ('county_id', models.IntegerField(null=True, blank=True)),
                ('city_id', models.IntegerField(null=True, blank=True)),
                ('state_pm', models.CharField(max_length=50, null=True, blank=True)),
                ('absolute_pm', models.FloatField(null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location_dist', django.contrib.gis.db.models.fields.PointField(srid=3857, null=True, blank=True)),
                ('sensor_length', models.FloatField(null=True, blank=True)),
                ('sensor_type', models.CharField(max_length=50, null=True, blank=True)),
                ('lanes', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('user_id_1', models.IntegerField(null=True, blank=True)),
                ('user_id_2', models.IntegerField(null=True, blank=True)),
                ('user_id_3', models.IntegerField(null=True, blank=True)),
                ('user_id_4', models.IntegerField(null=True, blank=True)),
                ('shape_length', models.FloatField(null=True, blank=True)),
                ('shape_area', models.FloatField(null=True, blank=True)),
                ('cnty', models.FloatField(null=True, blank=True)),
                ('taz_id', models.FloatField(null=True, blank=True)),
                ('pop_20', models.FloatField(null=True, blank=True)),
                ('hh_20', models.FloatField(null=True, blank=True)),
                ('emp_20', models.FloatField(null=True, blank=True)),
                ('pop_35', models.FloatField(null=True, blank=True)),
                ('hh_35', models.FloatField(null=True, blank=True)),
                ('emp_35', models.FloatField(null=True, blank=True)),
                ('cnty_1', models.FloatField(null=True, blank=True)),
                ('taz_id_1', models.FloatField(null=True, blank=True)),
                ('pop_08', models.FloatField(null=True, blank=True)),
                ('hh_08', models.FloatField(null=True, blank=True)),
                ('emp_08', models.FloatField(null=True, blank=True)),
                ('road_type', models.CharField(default=b'Freeway', max_length=50, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Waypoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(max_length=100, null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
                ('geom_dist', django.contrib.gis.db.models.fields.PolygonField(srid=3857, null=True, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('location_dist', django.contrib.gis.db.models.fields.PointField(srid=3857, null=True, blank=True)),
                ('density_id', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('origin_taz', 'destination_taz', 'od_route_index')]),
        ),
        migrations.AlterIndexTogether(
            name='route',
            index_together=set([('origin_taz', 'destination_taz')]),
        ),
        migrations.AddField(
            model_name='experimentsensor',
            name='sensor',
            field=models.ForeignKey(to='orm.Sensor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentroute',
            name='route',
            field=models.ForeignKey(to='orm.Route'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='experimentroute',
            index_together=set([('vector_index', 'description')]),
        ),
        migrations.AlterUniqueTogether(
            name='experiment2route',
            unique_together=set([('origin_taz', 'destination_taz', 'od_route_index')]),
        ),
        migrations.AlterIndexTogether(
            name='experiment2route',
            index_together=set([('origin_taz', 'destination_taz')]),
        ),
    ]
