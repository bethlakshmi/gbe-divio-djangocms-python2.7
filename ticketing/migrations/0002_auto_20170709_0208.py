# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brownpaperevents',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='brownpaperevents',
            name='display_icon',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AddField(
            model_name='brownpaperevents',
            name='title',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
