# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


def move_grade(apps, schema_editor):
    EventEvalGrade = apps.get_model('scheduler', 'EventEvalGrade')
    grade_convert = {
        'A': 4,
        'B': 3,
        'C': 2,
        'D': 1,
        'F': 0,
        'NA': None,
    }

    for grade in EventEvalGrade.objects.all():
        grade.new_answer = grade_convert[grade.answer]
        grade.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0008_auto_20180127_0237'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventevalgrade',
            name='new_answer',
            field=models.IntegerField(
                blank=True,
                choices=[(4, b'A'),
                         (3, b'B'),
                         (2, b'C'),
                         (1, b'D'),
                         (0, b'F'),
                         (None, b'NA')],
                null=True,
                validators=[django.core.validators.MinValueValidator(-1),
                            django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.RunPython(move_grade),
        migrations.RemoveField(
            model_name='eventevalgrade',
            name='answer',
        ),
        migrations.RenameField(
            model_name='eventevalgrade',
            old_name='new_answer',
            new_name='answer',
        ),
    ]
