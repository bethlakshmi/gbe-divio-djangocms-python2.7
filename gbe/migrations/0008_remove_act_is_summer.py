# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0007_conference_act_style'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='act',
            name='is_summer',
        ),
    ]
