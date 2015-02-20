# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phidata', '0003_auto_20141208_1910'),
    ]

    operations = [
        migrations.RenameField(
            model_name='route',
            old_name='route_id',
            new_name='id',
        ),
    ]
