# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0018_auto_20171230_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermessage',
            name='description',
            field=models.TextField(max_length=1000),
        ),
    ]
