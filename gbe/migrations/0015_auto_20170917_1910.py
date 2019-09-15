# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0007_auto_20161016_1055'),
        ('gbe', '0014_auto_20170829_0358'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evaluationcategory',
            options={'ordering': ['category'], 'verbose_name_plural': 'Evaluation Categories'},
        ),
        migrations.AddField(
            model_name='vendor',
            name='img',
            field=filer.fields.image.FilerImageField(related_name='image_vendor', to='filer.Image', null=True),
        ),
    ]
