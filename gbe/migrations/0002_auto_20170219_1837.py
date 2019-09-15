# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['e_title']},
        ),
        migrations.RenameField(
            model_name='biddable',
            old_name='description',
            new_name='b_description',
        ),
        migrations.RenameField(
            model_name='biddable',
            old_name='title',
            new_name='b_title',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='description',
            new_name='e_description',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='title',
            new_name='e_title',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='conference',
            new_name='e_conference',
        ),
        migrations.RenameField(
            model_name='biddable',
            old_name='conference',
            new_name='b_conference',
        ),
    ]
