# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0007_auto_20180122_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlabel',
            name='text',
            field=models.CharField(default=b'', max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='eventlabel',
            unique_together=set([('text', 'event')]),
        ),
    ]
