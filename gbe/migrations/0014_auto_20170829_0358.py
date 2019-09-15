# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0013_conferenceday_open_to_public'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(unique=True, max_length=128)),
                ('visible', models.BooleanField(default=True)),
                ('help_text', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FlexibleEvaluation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ranking', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(5)])),
                ('bid', models.ForeignKey(to='gbe.Biddable')),
                ('category', models.ForeignKey(to='gbe.EvaluationCategory')),
                ('evaluator', models.ForeignKey(to='gbe.Profile')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='flexibleevaluation',
            unique_together=set([('bid', 'evaluator', 'category')]),
        ),
    ]
