# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0017_remove_vendor_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='show',
            name='acts',
        ),
    ]
