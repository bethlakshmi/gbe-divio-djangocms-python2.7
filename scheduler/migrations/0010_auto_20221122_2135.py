# Generated by Django 3.2.16 on 2022-11-22 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0021_auto_20221122_2135'),
        ('scheduler', '0009_auto_20221117_0757'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='eventitem',
        ),
        migrations.DeleteModel(
            name='EventItem',
        ),
    ]
