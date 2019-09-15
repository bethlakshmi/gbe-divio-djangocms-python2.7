# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import gbe.expomodelfields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActBidEvaluation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'act bid evaluation',
                'verbose_name_plural': 'act bid evaluations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AudioInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('track_title', models.CharField(max_length=128, blank=True)),
                ('track_artist', models.CharField(max_length=123, blank=True)),
                ('track', models.FileField(upload_to=b'uploads/audio', blank=True)),
                ('track_duration', gbe.expomodelfields.DurationField(blank=True)),
                ('need_mic', models.BooleanField(default=False)),
                ('own_mic', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('confirm_no_music', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'audio info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AvailableInterest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interest', models.CharField(unique=True, max_length=128)),
                ('visible', models.BooleanField(default=True)),
                ('help_text', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Biddable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
                ('submitted', models.BooleanField(default=False)),
                ('accepted', models.IntegerField(default=0, choices=[(0, b'No Decision'), (1, b'Reject'), (2, b'Wait List'), (3, b'Accepted'), (4, b'Withdrawn'), (5, b'Duplicate')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'biddable item',
                'verbose_name_plural': 'biddable items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Act',
            fields=[
                ('actitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='scheduler.ActItem')),
                ('biddable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('video_link', models.URLField(blank=True)),
                ('video_choice', models.CharField(blank=True, max_length=2, choices=[(b'0', b"I don't have any video of myself performing"), (b'1', b"This is video of me but not the act I'm submitting"), (b'2', b'This is video of the act I would like to perform')])),
                ('shows_preferences', models.TextField(blank=True)),
                ('other_performance', models.TextField(blank=True)),
                ('why_you', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('gbe.biddable', 'scheduler.actitem'),
        ),
        migrations.CreateModel(
            name='BidEvaluation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.IntegerField(choices=[(1, b'Strong yes'), (2, b'Yes'), (3, b'Weak Yes'), (4, b'No Comment'), (5, b'Weak No'), (6, b'No'), (7, b'Strong No'), (-1, b'Abstain')])),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassProposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('proposal', models.TextField()),
                ('type', models.CharField(default=b'Class', max_length=20, choices=[(b'Class', b'Class'), (b'Panel', b'Panel'), (b'Either', b'Either')])),
                ('display', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('conference_name', models.CharField(max_length=128)),
                ('conference_slug', models.SlugField()),
                ('status', models.CharField(default=b'upcoming', max_length=50, choices=[(b'upcoming', b'upcoming'), (b'ongoing', b'ongoing'), (b'completed', b'completed')])),
                ('accepting_bids', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'conference',
                'verbose_name_plural': 'conferences',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConferenceDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField(blank=True)),
                ('conference', models.ForeignKey(to='gbe.Conference')),
            ],
            options={
                'ordering': ['day'],
                'verbose_name': 'Conference Day',
                'verbose_name_plural': 'Conference Days',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConferenceVolunteer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('how_volunteer', models.CharField(default=b'Any of the Above', max_length=20, choices=[(b'Teacher', b'Teacher'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Any of the Above', b'Any of the Above')])),
                ('qualification', models.TextField(blank=b'True')),
                ('volunteering', models.BooleanField(default=True)),
                ('bid', models.ForeignKey(to='gbe.ClassProposal')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Costume',
            fields=[
                ('biddable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('creator', models.CharField(max_length=128)),
                ('act_title', models.CharField(max_length=128, null=True, blank=True)),
                ('debut_date', models.CharField(max_length=128, null=True, blank=True)),
                ('active_use', models.BooleanField(default=True, choices=[(True, b'Yes'), (False, b'No')])),
                ('pieces', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('pasties', models.BooleanField(default=False, choices=[(True, b'Yes'), (False, b'No')])),
                ('dress_size', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('more_info', models.TextField(blank=True)),
                ('picture', models.FileField(upload_to=b'uploads/images', blank=True)),
            ],
            options={
            },
            bases=('gbe.biddable',),
        ),
        migrations.CreateModel(
            name='CueInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cue_sequence', models.PositiveIntegerField(default=0)),
                ('cue_off_of', models.TextField()),
                ('follow_spot', models.CharField(default=(b'White', b'White'), max_length=25, choices=[(b'White', b'White'), (b'Blue', b'Blue'), (b'OFF', b'OFF'), (b'Pink', b'Pink'), (b'Purple', b'Purple'), (b'Red', b'Red')])),
                ('center_spot', models.CharField(default=b'OFF', max_length=20, choices=[(b'Off', b'OFF'), (b'ON', b'ON')])),
                ('backlight', models.CharField(default=b'OFF', max_length=20, choices=[(b'Off', b'OFF'), (b'ON', b'ON')])),
                ('cyc_color', models.CharField(default=(b'Blue', b'Blue'), max_length=25, choices=[(b'Blue', b'Blue'), (b'Green', b'Green'), (b'OFF', b'OFF'), (b'Pink', b'Pink'), (b'Purple', b'Purple'), (b'Red', b'Red'), (b'White', b'White'), (b'Yellow', b'Yellow')])),
                ('wash', models.CharField(default=(b'White', b'White'), max_length=25, choices=[(b'White', b'White'), (b'Blue', b'Blue'), (b'Green', b'Green'), (b'OFF', b'OFF'), (b'Pink', b'Pink'), (b'Purple', b'Purple'), (b'Red', b'Red'), (b'Yellow', b'Yellow')])),
                ('sound_note', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'cue info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('eventitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='scheduler.EventItem')),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('blurb', models.TextField(blank=True)),
                ('duration', gbe.expomodelfields.DurationField()),
                ('notes', models.TextField(blank=True)),
                ('event_id', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ['title'],
            },
            bases=('scheduler.eventitem',),
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='gbe.Event')),
                ('biddable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('minimum_enrollment', models.IntegerField(default=1, blank=True)),
                ('maximum_enrollment', models.IntegerField(default=20, null=True, blank=True)),
                ('organization', models.CharField(max_length=128, blank=True)),
                ('type', models.CharField(default=b'Lecture', max_length=128, blank=True, choices=[(b'Lecture', b'Lecture'), (b'Movement', b'Movement'), (b'Panel', b'Panel'), (b'Workshop', b'Workshop')])),
                ('fee', models.IntegerField(default=0, null=True, blank=True)),
                ('other_teachers', models.CharField(max_length=128, blank=True)),
                ('length_minutes', models.IntegerField(default=60, blank=True, choices=[(60, b'60'), (90, b'90'), (120, b'120')])),
                ('history', models.TextField(blank=True)),
                ('run_before', models.TextField(blank=True)),
                ('schedule_constraints', models.TextField(blank=True)),
                ('avoided_constraints', models.TextField(blank=True)),
                ('space_needs', models.CharField(default=b'Please Choose an Option', max_length=128, blank=True, choices=[(b'Movement Class Floor', ((b'0', b"Don't Care about Floor"), (b'1', b'Carpet'), (b'2', b'Dance Floor'), (b'3', b'Both'))), (b'Lecture Class Setup', ((b'4', b"Don't Care about Seating"), (b'5', b'Lecture Style - tables and chairs face podium'), (b'6', b'Conversational - seating in a ring')))])),
                ('physical_restrictions', models.TextField(blank=True)),
                ('multiple_run', models.CharField(default=b'No', max_length=20, choices=[(b'Yes', b'Yes'), (b'No', b'No')])),
            ],
            options={
                'verbose_name_plural': 'classes',
            },
            bases=('gbe.biddable', 'gbe.event'),
        ),
        migrations.CreateModel(
            name='GenericEvent',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Event')),
                ('type', models.CharField(default=b'Special', max_length=128, choices=[(b'Special', b'Special Event'), (b'Volunteer', b'Volunteer Opportunity'), (b'Master', b'Master Class'), (b'Drop-In', b'Drop-In Class'), (b'Staff Area', b'Staff Area'), (b'Rehearsal Slot', b'Rehearsal Slot')])),
                ('volunteer_type', models.ForeignKey(blank=True, to='gbe.AvailableInterest', null=True)),
            ],
            options={
            },
            bases=('gbe.event',),
        ),
        migrations.CreateModel(
            name='LightingInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField(blank=True)),
                ('costume', models.TextField(blank=True)),
                ('specific_needs', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'lighting info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Performer',
            fields=[
                ('workeritem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.WorkerItem')),
                ('name', models.CharField(unique=True, max_length=100)),
                ('homepage', models.URLField(blank=True)),
                ('bio', models.TextField()),
                ('experience', models.PositiveIntegerField()),
                ('awards', models.TextField(blank=True)),
                ('promo_image', models.FileField(upload_to=b'uploads/images', blank=True)),
                ('festivals', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=('scheduler.workeritem',),
        ),
        migrations.CreateModel(
            name='Combo',
            fields=[
                ('performer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Performer')),
            ],
            options={
            },
            bases=('gbe.performer',),
        ),
        migrations.CreateModel(
            name='PerformerFestivals',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('festival', models.CharField(max_length=20, choices=[(b'GBE', b'The Great Burlesque Exposition'), (b'BHOF', b'Miss Exotic World/Burlesque Hall of Fame'), (b'NYBF', b'New York Burlesque Festival'), (b'NOBF', b'New Orleans Burlesque Festival'), (b'TBF', b'Texas Burlesque Festival')])),
                ('experience', models.CharField(default=b'No', max_length=20, choices=[(b'No', b'No'), (b'Yes', b'Yes'), (b'Won', b'Yes - and Won!')])),
                ('act', models.ForeignKey(to='gbe.Act')),
            ],
            options={
                'verbose_name_plural': 'performer festivals',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('performer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Performer')),
            ],
            options={
                'verbose_name_plural': 'personae',
            },
            bases=('gbe.performer',),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('workeritem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.WorkerItem')),
                ('display_name', models.CharField(max_length=128, blank=True)),
                ('purchase_email', models.CharField(default=b'', max_length=64, blank=True)),
                ('address1', models.CharField(max_length=128, blank=True)),
                ('address2', models.CharField(max_length=128, blank=True)),
                ('city', models.CharField(max_length=128, blank=True)),
                ('state', models.CharField(blank=True, max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming'), (b'OTHER', b'Other/Non-US')])),
                ('zip_code', models.CharField(max_length=10, blank=True)),
                ('country', models.CharField(max_length=128, blank=True)),
                ('phone', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(regex=b'(\\d{3}[-\\.]?\\d{3}[-\\.]?\\d{4})', message=b'Phone numbers must be in a standard US format, such as ###-###-###.')])),
                ('best_time', models.CharField(default=b'Any', max_length=50, blank=True, choices=[(b'Any', b'Any'), (b'Mornings', b'Mornings'), (b'Afternoons', b'Afternoons'), (b'Evenings', b'Evenings')])),
                ('how_heard', models.TextField(blank=True)),
                ('user_object', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['display_name'],
            },
            bases=('scheduler.workeritem',),
        ),
        migrations.CreateModel(
            name='ProfilePreferences',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('in_hotel', models.CharField(blank=True, max_length=10, choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Maybe', b'Maybe')])),
                ('inform_about', models.TextField(blank=True)),
                ('show_hotel_infobox', models.BooleanField(default=True)),
                ('profile', models.OneToOneField(related_name='preferences', to='gbe.Profile')),
            ],
            options={
                'verbose_name_plural': 'profile preferences',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('locationitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scheduler.LocationItem')),
                ('name', models.CharField(max_length=50)),
                ('capacity', models.IntegerField()),
                ('overbook_size', models.IntegerField()),
            ],
            options={
            },
            bases=('scheduler.locationitem',),
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('event_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Event')),
                ('cue_sheet', models.CharField(default=b'Theater', max_length=128, choices=[(b'Theater', b'Theater'), (b'Alternate', b'Alternate'), (b'None', b'None')])),
                ('acts', models.ManyToManyField(related_name='appearing_in', to='gbe.Act', blank=True)),
            ],
            options={
            },
            bases=('gbe.event',),
        ),
        migrations.CreateModel(
            name='ShowVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.IntegerField(blank=True, null=True, choices=[(1, b'Strong yes'), (2, b'Yes'), (3, b'Weak Yes'), (4, b'No Comment'), (5, b'Weak No'), (6, b'No'), (7, b'Strong No'), (-1, b'Abstain')])),
                ('show', models.ForeignKey(blank=True, to='gbe.Show', null=True)),
            ],
            options={
                'verbose_name': 'show vote',
                'verbose_name_plural': 'show votes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StageInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('act_duration', gbe.expomodelfields.DurationField(blank=True)),
                ('intro_text', models.TextField(blank=True)),
                ('confirm', models.BooleanField(default=False)),
                ('set_props', models.BooleanField(default=False)),
                ('cue_props', models.BooleanField(default=False)),
                ('clear_props', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'stage info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TechInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('audio', models.OneToOneField(blank=True, to='gbe.AudioInfo')),
                ('lighting', models.OneToOneField(blank=True, to='gbe.LightingInfo')),
                ('stage', models.OneToOneField(blank=True, to='gbe.StageInfo')),
            ],
            options={
                'verbose_name_plural': 'tech info',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Troupe',
            fields=[
                ('performer_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Performer')),
                ('membership', models.ManyToManyField(related_name='troupes', to='gbe.Persona')),
            ],
            options={
            },
            bases=('gbe.performer',),
        ),
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summary', models.CharField(max_length=128)),
                ('description', models.TextField(max_length=500)),
                ('view', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('biddable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('website', models.URLField(blank=True)),
                ('physical_address', models.TextField()),
                ('publish_physical_address', models.BooleanField(default=False)),
                ('logo', models.FileField(upload_to=b'uploads/images', blank=True)),
                ('want_help', models.BooleanField(default=False, choices=[(True, b'Yes'), (False, b'No')])),
                ('help_description', models.TextField(blank=True)),
                ('help_times', models.TextField(blank=True)),
                ('profile', models.ForeignKey(to='gbe.Profile')),
            ],
            options={
            },
            bases=('gbe.biddable',),
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('biddable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('number_shifts', models.IntegerField(choices=[(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)])),
                ('availability', models.TextField(blank=True)),
                ('unavailability', models.TextField(blank=True)),
                ('opt_outs', models.TextField(blank=True)),
                ('pre_event', models.BooleanField(default=False, choices=[(True, b'Yes'), (False, b'No')])),
                ('background', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('gbe.biddable',),
        ),
        migrations.CreateModel(
            name='VolunteerInterest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rank', models.IntegerField(blank=True, choices=[(0, b'--------------'), (1, b'Not interested'), (2, b'Slightly interested'), (3, b'Neither interested nor disinterested'), (4, b'Somewhat interested'), (5, b'Strongly interested')])),
                ('interest', models.ForeignKey(to='gbe.AvailableInterest')),
                ('volunteer', models.ForeignKey(to='gbe.Volunteer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VolunteerWindow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.TimeField(blank=True)),
                ('end', models.TimeField(blank=True)),
                ('day', models.ForeignKey(to='gbe.ConferenceDay')),
            ],
            options={
                'ordering': ['day', 'start'],
                'verbose_name': 'Volunteer Window',
                'verbose_name_plural': 'Volunteer Windows',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='volunteerinterest',
            unique_together=set([('interest', 'volunteer')]),
        ),
        migrations.AddField(
            model_name='volunteer',
            name='available_windows',
            field=models.ManyToManyField(related_name='availablewindow_set', to='gbe.VolunteerWindow', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='volunteer',
            name='profile',
            field=models.ForeignKey(related_name='volunteering', to='gbe.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='volunteer',
            name='unavailable_windows',
            field=models.ManyToManyField(related_name='unavailablewindow_set', to='gbe.VolunteerWindow', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='usermessage',
            unique_together=set([('view', 'code')]),
        ),
        migrations.AddField(
            model_name='persona',
            name='performer_profile',
            field=models.ForeignKey(related_name='personae', to='gbe.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='performer',
            name='contact',
            field=models.ForeignKey(related_name='contact', to='gbe.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='default_location',
            field=models.ForeignKey(blank=True, to='gbe.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='conference',
            field=models.ForeignKey(related_name='conference_set', blank=True, to='gbe.Conference', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cueinfo',
            name='techinfo',
            field=models.ForeignKey(to='gbe.TechInfo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='costume',
            name='performer',
            field=models.ForeignKey(blank=True, to='gbe.Persona', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='costume',
            name='profile',
            field=models.ForeignKey(related_name='costumes', to='gbe.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conferencevolunteer',
            name='presenter',
            field=models.ForeignKey(related_name='conf_volunteer', to='gbe.Persona'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='combo',
            name='membership',
            field=models.ManyToManyField(related_name='combos', to='gbe.Persona'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classproposal',
            name='conference',
            field=models.ForeignKey(blank=True, to='gbe.Conference', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(related_name='is_teaching', to='gbe.Persona'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bidevaluation',
            name='bid',
            field=models.ForeignKey(to='gbe.Biddable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bidevaluation',
            name='evaluator',
            field=models.ForeignKey(to='gbe.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='biddable',
            name='conference',
            field=models.ForeignKey(related_name='conference_set', blank=True, to='gbe.Conference', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='bid',
            field=models.ForeignKey(to='gbe.Act'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='evaluator',
            field=models.ForeignKey(to='gbe.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='primary_vote',
            field=models.ForeignKey(related_name='primary_vote', blank=True, to='gbe.ShowVote', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='secondary_vote',
            field=models.ForeignKey(related_name='secondary_vote', blank=True, to='gbe.ShowVote', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='performer',
            field=models.ForeignKey(related_name='acts', blank=True, to='gbe.Performer', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='act',
            name='tech',
            field=models.OneToOneField(blank=True, to='gbe.TechInfo'),
            preserve_default=True,
        ),
    ]
