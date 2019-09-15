# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gbe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrownPaperEvents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bpt_event_id', models.CharField(max_length=10)),
                ('primary', models.BooleanField(default=False)),
                ('act_submission_event', models.BooleanField(default=False, verbose_name=b'Act Fee')),
                ('vendor_submission_event', models.BooleanField(default=False, verbose_name=b'Vendor Fee')),
                ('include_conference', models.BooleanField(default=False)),
                ('include_most', models.BooleanField(default=False)),
                ('badgeable', models.BooleanField(default=False)),
                ('ticket_style', models.CharField(max_length=50, blank=True)),
                ('conference', models.ForeignKey(related_name='ticketing_item', blank=True, to='gbe.Conference', null=True)),
                ('linked_events', models.ManyToManyField(related_name='ticketing_item', to='gbe.Event', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Brown Paper Events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BrownPaperSettings',
            fields=[
                ('developer_token', models.CharField(max_length=15, serialize=False, primary_key=True)),
                ('client_username', models.CharField(max_length=30)),
                ('last_poll_time', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'Brown Paper Settings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CheckListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(unique=True, max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EligibilityCondition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Purchaser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('zip', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=50)),
                ('matched_to_user', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoleEligibilityCondition',
            fields=[
                ('eligibilitycondition_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ticketing.EligibilityCondition')),
                ('role', models.CharField(max_length=25, choices=[(b'Teacher', b'Teacher'), (b'Performer', b'Performer'), (b'Volunteer', b'Volunteer'), (b'Panelist', b'Panelist'), (b'Moderator', b'Moderator'), (b'Staff Lead', b'Staff Lead'), (b'Technical Director', b'Technical Director'), (b'Producer', b'Producer')])),
            ],
            options={
            },
            bases=('ticketing.eligibilitycondition',),
        ),
        migrations.CreateModel(
            name='RoleExclusion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=25, choices=[(b'Teacher', b'Teacher'), (b'Performer', b'Performer'), (b'Volunteer', b'Volunteer'), (b'Panelist', b'Panelist'), (b'Moderator', b'Moderator'), (b'Staff Lead', b'Staff Lead'), (b'Technical Director', b'Technical Director'), (b'Producer', b'Producer')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketingEligibilityCondition',
            fields=[
                ('eligibilitycondition_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='ticketing.EligibilityCondition')),
            ],
            options={
            },
            bases=('ticketing.eligibilitycondition',),
        ),
        migrations.CreateModel(
            name='TicketingExclusion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('condition', models.ForeignKey(related_name='ticketing_ticketingexclusion', to='ticketing.EligibilityCondition')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TicketItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticket_id', models.CharField(max_length=30)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('cost', models.DecimalField(max_digits=20, decimal_places=2)),
                ('datestamp', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(max_length=30)),
                ('live', models.BooleanField(default=False)),
                ('has_coupon', models.BooleanField(default=False)),
                ('bpt_event', models.ForeignKey(related_name='ticketitems', blank=True, to='ticketing.BrownPaperEvents')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=20, decimal_places=2)),
                ('order_date', models.DateTimeField()),
                ('shipping_method', models.CharField(max_length=50)),
                ('order_notes', models.TextField()),
                ('reference', models.CharField(max_length=30)),
                ('payment_source', models.CharField(max_length=30)),
                ('import_date', models.DateTimeField(auto_now=True)),
                ('purchaser', models.ForeignKey(to='ticketing.Purchaser')),
                ('ticket_item', models.ForeignKey(to='ticketing.TicketItem')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ticketingexclusion',
            name='tickets',
            field=models.ManyToManyField(to='ticketing.TicketItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ticketingeligibilitycondition',
            name='tickets',
            field=models.ManyToManyField(to='ticketing.TicketItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='roleexclusion',
            name='condition',
            field=models.ForeignKey(related_name='ticketing_roleexclusion', to='ticketing.EligibilityCondition'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='roleexclusion',
            name='event',
            field=models.ForeignKey(blank=True, to='gbe.Event', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eligibilitycondition',
            name='checklistitem',
            field=models.ForeignKey(related_name='ticketing_eligibilitycondition', to='ticketing.CheckListItem'),
            preserve_default=True,
        ),
    ]
