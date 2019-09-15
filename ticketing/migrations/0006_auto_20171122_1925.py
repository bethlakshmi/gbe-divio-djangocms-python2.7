# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0005_eventdetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brownpaperevents',
            name='bpt_event_id',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
