# Generated by Django 3.2.16 on 2022-11-13 21:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0004_auto_20210708_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='scheduler.event',
                related_name='children'),
        ),
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(null=True),
        ),
    ]