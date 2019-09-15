# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0003_auto_20170709_0211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticketitem',
            name='description',
        ),
    ]
