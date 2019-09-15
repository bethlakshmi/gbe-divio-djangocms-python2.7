# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0019_auto_20180117_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('default_volunteers', models.IntegerField(default=b'1', null=True, blank=True)),
                ('conference', models.ForeignKey(to='gbe.Conference')),
                ('default_location', models.ForeignKey(blank=True, to='gbe.Room', null=True)),
                ('staff_lead', models.ForeignKey(blank=True, to='gbe.Profile', null=True)),
            ],
            options={
                'ordering': ['conference', 'title'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='staffarea',
            unique_together=set([('title', 'conference'), ('slug', 'conference')]),
        ),
    ]
