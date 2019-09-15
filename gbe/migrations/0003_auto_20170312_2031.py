# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0002_auto_20170219_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='biddable',
            name='b_conference',
            field=models.ForeignKey(related_name='b_conference_set', blank=True, to='gbe.Conference', null=True),
        ),
        migrations.AlterField(
            model_name='classproposal',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='e_conference',
            field=models.ForeignKey(related_name='e_conference_set', blank=True, to='gbe.Conference', null=True),
        ),
    ]
