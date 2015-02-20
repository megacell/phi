# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('phidata', '0004_auto_20141208_1912'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TAZ',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
