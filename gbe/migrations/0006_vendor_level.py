# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-02-06 08:31


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0005_auto_20191229_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='level',
            field=models.CharField(blank=True,
                                   choices=[(b'Featured', b'Featured')],
                                   default=b'',
                                   max_length=128),
        ),
    ]
