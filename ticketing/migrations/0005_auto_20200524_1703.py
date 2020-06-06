# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-24 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0004_auto_20200422_2149'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayPalSettings',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('business_email', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'PayPal Settings',
            },
        ),
        migrations.AddField(
            model_name='ticketitem',
            name='add_on',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ticketitem',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ticketitem',
            name='is_minimum',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ticketitem',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='custom',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='invoice',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
