# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_description(apps, schema_editor):
    TicketItems = apps.get_model('ticketing', 'TicketItem')
    for item in TicketItems.objects.all():
        item.bpt_event.description = item.description
        item.bpt_event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0002_auto_20170709_0208'),
    ]

    operations = [
        migrations.RunPython(move_description),
    ]
