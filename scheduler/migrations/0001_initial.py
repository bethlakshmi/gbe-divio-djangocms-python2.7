# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventItem',
            fields=[
                ('eventitem_id', models.AutoField(serialize=False, primary_key=True)),
                ('visible', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ordering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('resource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.Resource')),
            ],
            options={
            },
            bases=('scheduler.resource',),
        ),
        migrations.CreateModel(
            name='ActResource',
            fields=[
                ('resource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.Resource')),
            ],
            options={
            },
            bases=('scheduler.resource',),
        ),
        migrations.CreateModel(
            name='ResourceItem',
            fields=[
                ('resourceitem_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LocationItem',
            fields=[
                ('resourceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.ResourceItem')),
            ],
            options={
            },
            bases=('scheduler.resourceitem',),
        ),
        migrations.CreateModel(
            name='ActItem',
            fields=[
                ('resourceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.ResourceItem')),
            ],
            options={
            },
            bases=('scheduler.resourceitem',),
        ),
        migrations.CreateModel(
            name='Schedulable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name_plural': 'Schedulable Items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceAllocation',
            fields=[
                ('schedulable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.Schedulable')),
            ],
            options={
            },
            bases=('scheduler.schedulable',),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('schedulable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.Schedulable')),
                ('starttime', models.DateTimeField(blank=True)),
                ('max_volunteer', models.PositiveIntegerField(default=0)),
                ('eventitem', models.ForeignKey(related_name='scheduler_events', to='scheduler.EventItem')),
            ],
            options={
            },
            bases=('scheduler.schedulable',),
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('resource_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.Resource')),
                ('role', models.CharField(blank=True, max_length=50, choices=[(b'Teacher', b'Teacher'), (b'Performer', b'Performer'), (b'Volunteer', b'Volunteer'), (b'Panelist', b'Panelist'), (b'Moderator', b'Moderator'), (b'Staff Lead', b'Staff Lead'), (b'Technical Director', b'Technical Director'), (b'Producer', b'Producer')])),
            ],
            options={
            },
            bases=('scheduler.resource',),
        ),
        migrations.CreateModel(
            name='WorkerItem',
            fields=[
                ('resourceitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.ResourceItem')),
            ],
            options={
            },
            bases=('scheduler.resourceitem',),
        ),
        migrations.AddField(
            model_name='worker',
            name='_item',
            field=models.ForeignKey(to='scheduler.WorkerItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourceallocation',
            name='event',
            field=models.ForeignKey(related_name='resources_allocated', to='scheduler.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourceallocation',
            name='resource',
            field=models.ForeignKey(related_name='allocations', to='scheduler.Resource'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ordering',
            name='allocation',
            field=models.OneToOneField(to='scheduler.ResourceAllocation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='_item',
            field=models.ForeignKey(to='scheduler.LocationItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='label',
            name='allocation',
            field=models.OneToOneField(to='scheduler.ResourceAllocation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventcontainer',
            name='child_event',
            field=models.OneToOneField(related_name='container_event', to='scheduler.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventcontainer',
            name='parent_event',
            field=models.ForeignKey(related_name='contained_events', to='scheduler.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actresource',
            name='_item',
            field=models.ForeignKey(to='scheduler.ActItem'),
            preserve_default=True,
        ),
    ]
