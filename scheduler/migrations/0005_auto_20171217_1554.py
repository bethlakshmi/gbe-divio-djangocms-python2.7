# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0004_create_event_labels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='role',
            field=models.CharField(blank=True, max_length=50, choices=[(b'Interested', b'Interested'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Performer', b'Performer'), (b'Producer', b'Producer'), (b'Staff Lead', b'Staff Lead'), (b'Teacher', b'Teacher'), (b'Technical Director', b'Technical Director'), (b'Volunteer', b'Volunteer')]),
        ),
    ]
