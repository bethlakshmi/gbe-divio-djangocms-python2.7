# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0006_act_is_summer'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='act_style',
            field=models.CharField(default=b'normal', max_length=50, choices=[(b'normal', b'normal'), (b'summer', b'summer')]),
        ),
    ]
