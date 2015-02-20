# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phidata', '0002_routes'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Routes',
            new_name='Route',
        ),
    ]
