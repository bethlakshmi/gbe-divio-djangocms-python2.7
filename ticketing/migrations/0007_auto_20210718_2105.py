# Generated by Django 3.0.14 on 2021-07-18 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0006_auto_20210706_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roleeligibilitycondition',
            name='role',
            field=models.CharField(choices=[('Interested', 'Interested'), ('Moderator', 'Moderator'), ('Panelist', 'Panelist'), ('Performer', 'Performer'), ('Producer', 'Producer'), ('Stage Manager', 'Stage Manager'), ('Staff Lead', 'Staff Lead'), ('Teacher', 'Teacher'), ('Technical Director', 'Technical Director'), ('Volunteer', 'Volunteer'), ('Rejected', 'Rejected'), ('Waitlisted', 'Waitlisted'), ('Pending Volunteer', 'Pending Volunteer')], max_length=25),
        ),
        migrations.AlterField(
            model_name='roleexclusion',
            name='role',
            field=models.CharField(choices=[('Interested', 'Interested'), ('Moderator', 'Moderator'), ('Panelist', 'Panelist'), ('Performer', 'Performer'), ('Producer', 'Producer'), ('Stage Manager', 'Stage Manager'), ('Staff Lead', 'Staff Lead'), ('Teacher', 'Teacher'), ('Technical Director', 'Technical Director'), ('Volunteer', 'Volunteer'), ('Rejected', 'Rejected'), ('Waitlisted', 'Waitlisted'), ('Pending Volunteer', 'Pending Volunteer')], max_length=25),
        ),
    ]
