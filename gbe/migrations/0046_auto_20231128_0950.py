# Generated by Django 3.2.18 on 2023-11-28 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0045_new_class_settings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='profilepreferences',
            name='show_hotel_infobox',
        ),
    ]
