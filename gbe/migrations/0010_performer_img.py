# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0007_auto_20161016_1055'),
        ('gbe', '0009_actcastingoption'),
    ]

    operations = [
        migrations.AddField(
            model_name='performer',
            name='img',
            field=filer.fields.image.FilerImageField(
                related_name='image_performer',
                to='filer.Image',
                null=True),
        ),
    ]
