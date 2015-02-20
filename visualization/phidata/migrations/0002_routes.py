# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('phidata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Routes',
            fields=[
                ('route_id', models.IntegerField(serialize=False, primary_key=True)),
                ('links', djorm_pgarray.fields.ArrayField(default=None, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
