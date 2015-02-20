# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('phidata', '0005_cell_taz'),
    ]

    operations = [
        migrations.CreateModel(
            name='CellRouteMap',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('routes', djorm_pgarray.fields.ArrayField(default=None, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
