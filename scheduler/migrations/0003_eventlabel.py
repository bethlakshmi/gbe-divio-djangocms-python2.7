# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0002_actresource_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(default=b'')),
                ('event', models.ForeignKey(to='scheduler.Event')),
            ],
        ),
    ]
