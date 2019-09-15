# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0005_auto_20170414_0234'),
    ]

    operations = [
        migrations.AddField(
            model_name='act',
            name='is_summer',
            field=models.BooleanField(default=False),
        ),
    ]
