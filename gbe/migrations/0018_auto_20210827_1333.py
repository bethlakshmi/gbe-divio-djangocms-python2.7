# Generated by Django 3.0.14 on 2021-08-27 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0017_auto_20210814_0858'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='act',
            options={'permissions': [('assign_act', 'Coordinate acts - assign status, book, and create for others'), ('review_act', "Can read other's acts and create reviews.")]},
        ),
    ]