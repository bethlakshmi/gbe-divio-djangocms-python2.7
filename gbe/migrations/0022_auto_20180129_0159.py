# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0021_auto_20180127_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericevent',
            name='type',
            field=models.CharField(default=b'Special', max_length=128, choices=[(b'Special', b'Special Event'), (b'Volunteer', b'Volunteer Opportunity'), (b'Master', b'Master Class'), (b'Drop-In', b'Drop-In Class'), (b'Rehearsal Slot', b'Rehearsal Slot')]),
        ),
    ]
