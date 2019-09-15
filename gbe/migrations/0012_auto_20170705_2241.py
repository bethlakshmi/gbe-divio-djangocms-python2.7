# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0011_convert_persona_image_to_filer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actcastingoption',
            options={'ordering': ['display_order']},
        ),
        migrations.RemoveField(
            model_name='performer',
            name='promo_image',
        ),
    ]
