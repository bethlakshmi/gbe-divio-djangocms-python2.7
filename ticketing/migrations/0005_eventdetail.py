# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0004_remove_ticketitem_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detail', models.CharField(max_length=50, blank=True)),
                ('bpt_event', models.ForeignKey(to='ticketing.BrownPaperEvents', blank=True)),
            ],
        ),
    ]
