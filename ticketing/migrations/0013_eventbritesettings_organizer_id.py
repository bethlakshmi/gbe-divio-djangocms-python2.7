# Generated by Django 3.2.16 on 2023-03-12 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0012_auto_20221118_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventbritesettings',
            name='organizer_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
