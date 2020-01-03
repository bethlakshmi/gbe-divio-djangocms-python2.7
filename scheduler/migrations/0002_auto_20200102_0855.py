# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-02 08:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='approval_needed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='worker',
            name='role',
            field=models.CharField(blank=True, choices=[(b'Interested', b'Interested'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Performer', b'Performer'), (b'Producer', b'Producer'), (b'Staff Lead', b'Staff Lead'), (b'Teacher', b'Teacher'), (b'Technical Director', b'Technical Director'), (b'Volunteer', b'Volunteer'), (b'Pending Volunteer', b'Pending Volunteer')], max_length=50),
        ),
    ]
