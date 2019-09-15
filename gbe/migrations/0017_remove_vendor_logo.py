# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0016_convert_vendor_image_to_filer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor',
            name='logo',
        ),
    ]
