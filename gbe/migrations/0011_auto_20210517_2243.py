# Generated by Django 3.0.12 on 2021-05-17 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0010_auto_20210429_1745'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='volunteerinterest',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='volunteerinterest',
            name='interest',
        ),
        migrations.RemoveField(
            model_name='volunteerinterest',
            name='volunteer',
        ),
        migrations.RemoveField(
            model_name='genericevent',
            name='volunteer_type',
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='availability',
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='background',
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='number_shifts',
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='opt_outs',
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='pre_event',
        ),
        migrations.RemoveField(
            model_name='volunteer',
            name='unavailability',
        ),
        migrations.DeleteModel(
            name='AvailableInterest',
        ),
        migrations.DeleteModel(
            name='VolunteerInterest',
        ),
    ]
