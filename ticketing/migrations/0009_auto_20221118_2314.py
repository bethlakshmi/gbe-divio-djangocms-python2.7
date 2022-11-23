# Generated by Django 3.2.16 on 2022-11-18 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0020_alter_profile_phone'),
        ('scheduler', '0009_auto_20221117_0757'),
        ('ticketing', '0008_auto_20210827_1004'),
    ]

    operations = [
        migrations.AddField(
            model_name='roleexclusion',
            name='event_2',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='scheduler.event'),
        ),
        migrations.AddField(
            model_name='ticketingevents',
            name='linked_events_2',
            field=models.ManyToManyField(blank=True, to='scheduler.Event'),
        ),
    ]