# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0006_auto_20171122_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roleeligibilitycondition',
            name='role',
            field=models.CharField(max_length=25, choices=[(b'Interested', b'Interested'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Performer', b'Performer'), (b'Producer', b'Producer'), (b'Staff Lead', b'Staff Lead'), (b'Teacher', b'Teacher'), (b'Technical Director', b'Technical Director'), (b'Volunteer', b'Volunteer')]),
        ),
        migrations.AlterField(
            model_name='roleexclusion',
            name='role',
            field=models.CharField(max_length=25, choices=[(b'Interested', b'Interested'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Performer', b'Performer'), (b'Producer', b'Producer'), (b'Staff Lead', b'Staff Lead'), (b'Teacher', b'Teacher'), (b'Technical Director', b'Technical Director'), (b'Volunteer', b'Volunteer')]),
        ),
    ]
