# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0004_emailtemplatesender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteer',
            name='background',
            field=models.TextField(),
        ),
    ]
