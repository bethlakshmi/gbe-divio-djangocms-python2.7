# Generated by Django 3.2.18 on 2023-05-16 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0013_remove_worker_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkerItem',
            fields=[
                ('resourceitem_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='scheduler.resourceitem')),
            ],
            bases=('scheduler.resourceitem',),
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('resource_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True, primary_key=True,
                    serialize=False,
                    to='scheduler.resource')),
                ('role', models.CharField(
                    blank=True,
                    choices=[('Interested', 'Interested'),
                             ('Moderator', 'Moderator'),
                             ('Panelist', 'Panelist'),
                             ('Performer', 'Performer'),
                             ('Producer', 'Producer'),
                             ('Stage Manager', 'Stage Manager'),
                             ('Staff Lead', 'Staff Lead'),
                             ('Teacher', 'Teacher'),
                             ('Technical Director', 'Technical Director'),
                             ('Volunteer', 'Volunteer'),
                             ('Rejected', 'Rejected'),
                             ('Waitlisted', 'Waitlisted'),
                             ('Pending Volunteer', 'Pending Volunteer')],
                    max_length=50)),
                ('_item', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='scheduler.workeritem')),
            ],
            bases=('scheduler.resource',),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('text', models.TextField(default='')),
                ('allocation', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='scheduler.resourceallocation')),
            ],
        ),
    ]
