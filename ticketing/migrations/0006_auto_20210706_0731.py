# Generated by Django 3.0.14 on 2021-07-06 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0005_syncstatus'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='syncstatus',
            options={'verbose_name_plural': 'Sync Statuses'},
        ),
        migrations.AddField(
            model_name='ticketitem',
            name='special_comp',
            field=models.BooleanField(default=False),
        ),
    ]
