# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-06-18 20:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0005_auto_20200524_1703'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticketitem',
            options={'ordering': ['cost']},
        ),
        migrations.RemoveField(
            model_name='brownpaperevents',
            name='primary',
        ),
    ]
