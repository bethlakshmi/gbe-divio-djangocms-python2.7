# Generated by Django 3.2.16 on 2022-11-22 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0021_auto_20221122_2135'),
        ('scheduler', '0010_auto_20221122_2135'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='GenericEvent',
        ),
        migrations.DeleteModel(
            name='Show',
        ),
        migrations.DeleteModel(
            name='ShowVote',
        ),
    ]
