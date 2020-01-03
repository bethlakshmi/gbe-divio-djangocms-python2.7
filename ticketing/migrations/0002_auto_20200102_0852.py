# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-02 08:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roleeligibilitycondition',
            name='role',
            field=models.CharField(choices=[(b'Interested', b'Interested'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Performer', b'Performer'), (b'Producer', b'Producer'), (b'Staff Lead', b'Staff Lead'), (b'Teacher', b'Teacher'), (b'Technical Director', b'Technical Director'), (b'Volunteer', b'Volunteer'), (b'Pending Volunteer', b'Pending Volunteer')], max_length=25),
        ),
        migrations.AlterField(
            model_name='roleexclusion',
            name='role',
            field=models.CharField(choices=[(b'Interested', b'Interested'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Performer', b'Performer'), (b'Producer', b'Producer'), (b'Staff Lead', b'Staff Lead'), (b'Teacher', b'Teacher'), (b'Technical Director', b'Technical Director'), (b'Volunteer', b'Volunteer'), (b'Pending Volunteer', b'Pending Volunteer')], max_length=25),
        ),
    ]
