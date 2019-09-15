# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0008_remove_act_is_summer'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActCastingOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('casting', models.CharField(unique=True, max_length=50)),
                ('show_as_special', models.BooleanField(default=True)),
                ('display_order', models.IntegerField(unique=True)),
            ],
        ),
    ]
