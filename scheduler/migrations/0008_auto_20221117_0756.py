# Generated by Django 3.2.16 on 2022-11-17 07:56

from django.db import migrations, models
from datetime import timedelta


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0007_delete_eventcontainer'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='blurb',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='title',
            field=models.CharField(default='placeholder', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='event_style',
            field=models.CharField(default='not_set!', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='connected_class',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='event',
            name='connected_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='length',
            field=models.DurationField(default=timedelta(minutes=0)),
            preserve_default=False,
        ),
    ]
