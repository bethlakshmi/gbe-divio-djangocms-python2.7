# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0006_auto_20180102_1343'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventevalquestion',
            options={'ordering': ['order']},
        ),
    ]
