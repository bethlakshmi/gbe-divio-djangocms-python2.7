# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-19 08:25
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.image


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduler', '0001_initial'),
        ('post_office', '0008_attachment_headers'),
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActBidEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'act bid evaluation',
                'verbose_name_plural': 'act bid evaluations',
            },
        ),
        migrations.CreateModel(
            name='ActCastingOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('casting', models.CharField(max_length=50, unique=True)),
                ('show_as_special', models.BooleanField(default=True)),
                ('display_order', models.IntegerField(unique=True)),
            ],
            options={
                'ordering': ['display_order'],
            },
        ),
        migrations.CreateModel(
            name='AudioInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_title', models.CharField(blank=True, max_length=128)),
                ('track_artist', models.CharField(blank=True, max_length=123)),
                ('track', models.FileField(blank=True, upload_to=b'uploads/audio')),
                ('track_duration', models.DurationField(blank=True)),
                ('need_mic', models.BooleanField(default=False)),
                ('own_mic', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('confirm_no_music', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'audio info',
            },
        ),
        migrations.CreateModel(
            name='AvailableInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.CharField(max_length=128, unique=True)),
                ('visible', models.BooleanField(default=True)),
                ('help_text', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Biddable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('b_title', models.CharField(max_length=128)),
                ('b_description', models.TextField(blank=True)),
                ('submitted', models.BooleanField(default=False)),
                ('accepted', models.IntegerField(choices=[(0, b'No Decision'), (1, b'Reject'), (2, b'Wait List'), (3, b'Accepted'), (4, b'Withdrawn'), (5, b'Duplicate')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'biddable item',
                'verbose_name_plural': 'biddable items',
            },
        ),
        migrations.CreateModel(
            name='BidEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(choices=[(1, b'Strong yes'), (2, b'Yes'), (3, b'Weak Yes'), (4, b'No Comment'), (5, b'Weak No'), (6, b'No'), (7, b'Strong No'), (-1, b'Abstain')])),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClassProposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('name', models.CharField(blank=True, max_length=128)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('proposal', models.TextField()),
                ('type', models.CharField(choices=[(b'Class', b'Class'), (b'Panel', b'Panel'), (b'Either', b'Either')], default=b'Class', max_length=20)),
                ('display', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conference_name', models.CharField(max_length=128)),
                ('conference_slug', models.SlugField()),
                ('status', models.CharField(choices=[(b'upcoming', b'upcoming'), (b'ongoing', b'ongoing'), (b'completed', b'completed')], default=b'upcoming', max_length=50)),
                ('accepting_bids', models.BooleanField(default=False)),
                ('act_style', models.CharField(choices=[(b'normal', b'normal'), (b'summer', b'summer')], default=b'normal', max_length=50)),
            ],
            options={
                'verbose_name': 'conference',
                'verbose_name_plural': 'conferences',
            },
        ),
        migrations.CreateModel(
            name='ConferenceDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField(blank=True)),
                ('open_to_public', models.BooleanField(default=True)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Conference')),
            ],
            options={
                'ordering': ['day'],
                'verbose_name': 'Conference Day',
                'verbose_name_plural': 'Conference Days',
            },
        ),
        migrations.CreateModel(
            name='ConferenceVolunteer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('how_volunteer', models.CharField(choices=[(b'Teacher', b'Teacher'), (b'Moderator', b'Moderator'), (b'Panelist', b'Panelist'), (b'Any of the Above', b'Any of the Above')], default=b'Any of the Above', max_length=20)),
                ('qualification', models.TextField(blank=b'True')),
                ('volunteering', models.BooleanField(default=True)),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.ClassProposal')),
            ],
        ),
        migrations.CreateModel(
            name='CueInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cue_sequence', models.PositiveIntegerField(default=0)),
                ('cue_off_of', models.TextField()),
                ('follow_spot', models.CharField(choices=[(b'White', b'White'), (b'Blue', b'Blue'), (b'OFF', b'OFF'), (b'Pink', b'Pink'), (b'Purple', b'Purple'), (b'Red', b'Red')], default=(b'White', b'White'), max_length=25)),
                ('center_spot', models.CharField(choices=[(b'Off', b'OFF'), (b'ON', b'ON')], default=b'OFF', max_length=20)),
                ('backlight', models.CharField(choices=[(b'Off', b'OFF'), (b'ON', b'ON')], default=b'OFF', max_length=20)),
                ('cyc_color', models.CharField(choices=[(b'Blue', b'Blue'), (b'Green', b'Green'), (b'OFF', b'OFF'), (b'Pink', b'Pink'), (b'Purple', b'Purple'), (b'Red', b'Red'), (b'White', b'White'), (b'Yellow', b'Yellow')], default=(b'Blue', b'Blue'), max_length=25)),
                ('wash', models.CharField(choices=[(b'White', b'White'), (b'Blue', b'Blue'), (b'Green', b'Green'), (b'OFF', b'OFF'), (b'Pink', b'Pink'), (b'Purple', b'Purple'), (b'Red', b'Red'), (b'Yellow', b'Yellow')], default=(b'White', b'White'), max_length=25)),
                ('sound_note', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'cue info',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplateSender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_email', models.EmailField(max_length=254)),
                ('template', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='post_office.EmailTemplate')),
            ],
            options={
                'ordering': ['template__name'],
            },
        ),
        migrations.CreateModel(
            name='EvaluationCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=128, unique=True)),
                ('visible', models.BooleanField(default=True)),
                ('help_text', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['category'],
                'verbose_name_plural': 'Evaluation Categories',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('eventitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='scheduler.EventItem')),
                ('e_title', models.CharField(max_length=128)),
                ('e_description', models.TextField()),
                ('blurb', models.TextField(blank=True)),
                ('duration', models.DurationField()),
                ('notes', models.TextField(blank=True)),
                ('event_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'ordering': ['e_title'],
            },
            bases=('scheduler.eventitem',),
        ),
        migrations.CreateModel(
            name='FlexibleEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ranking', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.CreateModel(
            name='LightingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True)),
                ('costume', models.TextField(blank=True)),
                ('specific_needs', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'lighting info',
            },
        ),
        migrations.CreateModel(
            name='Performer',
            fields=[
                ('workeritem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scheduler.WorkerItem')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('homepage', models.URLField(blank=True)),
                ('bio', models.TextField()),
                ('experience', models.PositiveIntegerField()),
                ('awards', models.TextField(blank=True)),
                ('festivals', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=('scheduler.workeritem',),
        ),
        migrations.CreateModel(
            name='PerformerFestivals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('festival', models.CharField(choices=[(b'GBE', b'The Great Burlesque Exposition'), (b'BHOF', b'Miss Exotic World/Burlesque Hall of Fame'), (b'NYBF', b'New York Burlesque Festival'), (b'NOBF', b'New Orleans Burlesque Festival'), (b'TBF', b'Texas Burlesque Festival')], max_length=20)),
                ('experience', models.CharField(choices=[(b'No', b'No'), (b'Yes', b'Yes'), (b'Won', b'Yes - and Won!')], default=b'No', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'performer festivals',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('workeritem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scheduler.WorkerItem')),
                ('display_name', models.CharField(blank=True, max_length=128)),
                ('purchase_email', models.CharField(blank=True, default=b'', max_length=64)),
                ('address1', models.CharField(blank=True, max_length=128)),
                ('address2', models.CharField(blank=True, max_length=128)),
                ('city', models.CharField(blank=True, max_length=128)),
                ('state', models.CharField(blank=True, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming'), (b'OTHER', b'Other/Non-US')], max_length=2)),
                ('zip_code', models.CharField(blank=True, max_length=10)),
                ('country', models.CharField(blank=True, max_length=128)),
                ('phone', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message=b'Phone numbers must be in a standard US format, such as ###-###-###.', regex=b'(\\d{3}[-\\.]?\\d{3}[-\\.]?\\d{4})')])),
                ('best_time', models.CharField(blank=True, choices=[(b'Any', b'Any'), (b'Mornings', b'Mornings'), (b'Afternoons', b'Afternoons'), (b'Evenings', b'Evenings')], default=b'Any', max_length=50)),
                ('how_heard', models.TextField(blank=True)),
                ('user_object', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['display_name'],
            },
            bases=('scheduler.workeritem',),
        ),
        migrations.CreateModel(
            name='ProfilePreferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_hotel', models.CharField(blank=True, choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Maybe', b'Maybe')], max_length=10)),
                ('inform_about', models.TextField(blank=True)),
                ('show_hotel_infobox', models.BooleanField(default=True)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='gbe.Profile')),
            ],
            options={
                'verbose_name_plural': 'profile preferences',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('locationitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scheduler.LocationItem')),
                ('name', models.CharField(max_length=50)),
                ('capacity', models.IntegerField()),
                ('overbook_size', models.IntegerField()),
            ],
            bases=('scheduler.locationitem',),
        ),
        migrations.CreateModel(
            name='ShowVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(blank=True, choices=[(1, b'Strong yes'), (2, b'Yes'), (3, b'Weak Yes'), (4, b'No Comment'), (5, b'Weak No'), (6, b'No'), (7, b'Strong No'), (-1, b'Abstain')], null=True)),
            ],
            options={
                'verbose_name': 'show vote',
                'verbose_name_plural': 'show votes',
            },
        ),
        migrations.CreateModel(
            name='StaffArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('default_volunteers', models.IntegerField(blank=True, default=b'1', null=True)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Conference')),
                ('default_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.Room')),
                ('staff_lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.Profile')),
            ],
            options={
                'ordering': ['conference', 'title'],
            },
        ),
        migrations.CreateModel(
            name='StageInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('act_duration', models.DurationField(blank=True)),
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
        ),
        migrations.CreateModel(
            name='TechInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.AudioInfo')),
                ('lighting', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.LightingInfo')),
                ('stage', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.StageInfo')),
            ],
            options={
                'verbose_name_plural': 'tech info',
            },
        ),
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.CharField(max_length=128)),
                ('description', models.TextField(max_length=1000)),
                ('view', models.CharField(max_length=128)),
                ('code', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='VolunteerInterest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField(blank=True, choices=[(0, b'--------------'), (1, b'Not interested'), (2, b'Slightly interested'), (3, b'Neither interested nor disinterested'), (4, b'Somewhat interested'), (5, b'Strongly interested')])),
                ('interest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.AvailableInterest')),
            ],
        ),
        migrations.CreateModel(
            name='VolunteerWindow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.TimeField(blank=True)),
                ('end', models.TimeField(blank=True)),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.ConferenceDay')),
            ],
            options={
                'ordering': ['day', 'start'],
                'verbose_name': 'Volunteer Window',
                'verbose_name_plural': 'Volunteer Windows',
            },
        ),
        migrations.CreateModel(
            name='Act',
            fields=[
                ('actitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='scheduler.ActItem')),
                ('biddable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('video_link', models.URLField(blank=True)),
                ('video_choice', models.CharField(blank=True, choices=[(b'0', b"I don't have any video of myself performing"), (b'1', b"This is video of me but not the act I'm submitting"), (b'2', b'This is video of the act I would like to perform')], max_length=2)),
                ('shows_preferences', models.TextField(blank=True)),
                ('other_performance', models.TextField(blank=True)),
                ('why_you', models.TextField(blank=True)),
            ],
            bases=('gbe.biddable', 'scheduler.actitem'),
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='gbe.Event')),
                ('biddable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('minimum_enrollment', models.IntegerField(blank=True, default=1)),
                ('maximum_enrollment', models.IntegerField(blank=True, default=20, null=True)),
                ('organization', models.CharField(blank=True, max_length=128)),
                ('type', models.CharField(blank=True, choices=[(b'Lecture', b'Lecture'), (b'Movement', b'Movement'), (b'Panel', b'Panel'), (b'Workshop', b'Workshop')], default=b'Lecture', max_length=128)),
                ('fee', models.IntegerField(blank=True, default=0, null=True)),
                ('other_teachers', models.CharField(blank=True, max_length=128)),
                ('length_minutes', models.IntegerField(blank=True, choices=[(60, b'60'), (90, b'90'), (120, b'120')], default=60)),
                ('history', models.TextField(blank=True)),
                ('run_before', models.TextField(blank=True)),
                ('schedule_constraints', models.TextField(blank=True)),
                ('avoided_constraints', models.TextField(blank=True)),
                ('space_needs', models.CharField(blank=True, choices=[(b'Movement Class Floor', ((b'0', b"Don't Care about Floor"), (b'1', b'Carpet'), (b'2', b'Dance Floor'), (b'3', b'Both'))), (b'Lecture Class Setup', ((b'4', b"Don't Care about Seating"), (b'5', b'Lecture Style - tables and chairs face podium'), (b'6', b'Conversational - seating in a ring')))], default=b'Please Choose an Option', max_length=128)),
                ('physical_restrictions', models.TextField(blank=True)),
                ('multiple_run', models.CharField(choices=[(b'Yes', b'Yes'), (b'No', b'No')], default=b'No', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'classes',
            },
            bases=('gbe.biddable', 'gbe.event'),
        ),
        migrations.CreateModel(
            name='Combo',
            fields=[
                ('performer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Performer')),
            ],
            bases=('gbe.performer',),
        ),
        migrations.CreateModel(
            name='Costume',
            fields=[
                ('biddable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('creator', models.CharField(max_length=128)),
                ('act_title', models.CharField(blank=True, max_length=128, null=True)),
                ('debut_date', models.CharField(blank=True, max_length=128, null=True)),
                ('active_use', models.BooleanField(choices=[(True, b'Yes'), (False, b'No')], default=True)),
                ('pieces', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('pasties', models.BooleanField(choices=[(True, b'Yes'), (False, b'No')], default=False)),
                ('dress_size', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)])),
                ('more_info', models.TextField(blank=True)),
                ('picture', models.FileField(blank=True, upload_to=b'uploads/images')),
            ],
            bases=('gbe.biddable',),
        ),
        migrations.CreateModel(
            name='GenericEvent',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Event')),
                ('type', models.CharField(choices=[(b'Special', b'Special Event'), (b'Volunteer', b'Volunteer Opportunity'), (b'Master', b'Master Class'), (b'Drop-In', b'Drop-In Class'), (b'Rehearsal Slot', b'Rehearsal Slot')], default=b'Special', max_length=128)),
                ('volunteer_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.AvailableInterest')),
            ],
            bases=('gbe.event',),
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('performer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Performer')),
                ('performer_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personae', to='gbe.Profile')),
            ],
            options={
                'verbose_name_plural': 'personae',
            },
            bases=('gbe.performer',),
        ),
        migrations.CreateModel(
            name='Show',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Event')),
                ('cue_sheet', models.CharField(choices=[(b'Theater', b'Theater'), (b'Alternate', b'Alternate'), (b'None', b'None')], default=b'Theater', max_length=128)),
            ],
            bases=('gbe.event',),
        ),
        migrations.CreateModel(
            name='Troupe',
            fields=[
                ('performer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Performer')),
                ('membership', models.ManyToManyField(related_name='troupes', to='gbe.Persona')),
            ],
            bases=('gbe.performer',),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('biddable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('website', models.URLField(blank=True)),
                ('physical_address', models.TextField()),
                ('publish_physical_address', models.BooleanField(default=False)),
                ('want_help', models.BooleanField(choices=[(True, b'Yes'), (False, b'No')], default=False)),
                ('help_description', models.TextField(blank=True)),
                ('help_times', models.TextField(blank=True)),
                ('img', filer.fields.image.FilerImageField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_vendor', to=settings.FILER_IMAGE_MODEL)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Profile')),
            ],
            bases=('gbe.biddable',),
        ),
        migrations.CreateModel(
            name='Volunteer',
            fields=[
                ('biddable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gbe.Biddable')),
                ('number_shifts', models.IntegerField(choices=[(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)])),
                ('availability', models.TextField(blank=True)),
                ('unavailability', models.TextField(blank=True)),
                ('opt_outs', models.TextField(blank=True)),
                ('pre_event', models.BooleanField(choices=[(True, b'Yes'), (False, b'No')], default=False)),
                ('background', models.TextField()),
                ('available_windows', models.ManyToManyField(blank=True, related_name='availablewindow_set', to='gbe.VolunteerWindow')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='volunteering', to='gbe.Profile')),
                ('unavailable_windows', models.ManyToManyField(blank=True, related_name='unavailablewindow_set', to='gbe.VolunteerWindow')),
            ],
            bases=('gbe.biddable',),
        ),
        migrations.AlterUniqueTogether(
            name='usermessage',
            unique_together=set([('view', 'code')]),
        ),
        migrations.AddField(
            model_name='performer',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact', to='gbe.Profile'),
        ),
        migrations.AddField(
            model_name='performer',
            name='img',
            field=filer.fields.image.FilerImageField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_performer', to=settings.FILER_IMAGE_MODEL),
        ),
        migrations.AddField(
            model_name='flexibleevaluation',
            name='bid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Biddable'),
        ),
        migrations.AddField(
            model_name='flexibleevaluation',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.EvaluationCategory'),
        ),
        migrations.AddField(
            model_name='flexibleevaluation',
            name='evaluator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Profile'),
        ),
        migrations.AddField(
            model_name='event',
            name='default_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.Room'),
        ),
        migrations.AddField(
            model_name='event',
            name='e_conference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='e_conference_set', to='gbe.Conference'),
        ),
        migrations.AddField(
            model_name='cueinfo',
            name='techinfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.TechInfo'),
        ),
        migrations.AddField(
            model_name='classproposal',
            name='conference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.Conference'),
        ),
        migrations.AddField(
            model_name='bidevaluation',
            name='bid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Biddable'),
        ),
        migrations.AddField(
            model_name='bidevaluation',
            name='evaluator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Profile'),
        ),
        migrations.AddField(
            model_name='biddable',
            name='b_conference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='b_conference_set', to='gbe.Conference'),
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='evaluator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Profile'),
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='primary_vote',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='primary_vote', to='gbe.ShowVote'),
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='secondary_vote',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='secondary_vote', to='gbe.ShowVote'),
        ),
        migrations.AddField(
            model_name='volunteerinterest',
            name='volunteer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Volunteer'),
        ),
        migrations.AlterUniqueTogether(
            name='staffarea',
            unique_together=set([('title', 'conference'), ('slug', 'conference')]),
        ),
        migrations.AddField(
            model_name='showvote',
            name='show',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.Show'),
        ),
        migrations.AddField(
            model_name='performerfestivals',
            name='act',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Act'),
        ),
        migrations.AlterUniqueTogether(
            name='flexibleevaluation',
            unique_together=set([('bid', 'evaluator', 'category')]),
        ),
        migrations.AddField(
            model_name='costume',
            name='performer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.Persona'),
        ),
        migrations.AddField(
            model_name='costume',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='costumes', to='gbe.Profile'),
        ),
        migrations.AddField(
            model_name='conferencevolunteer',
            name='presenter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conf_volunteer', to='gbe.Persona'),
        ),
        migrations.AddField(
            model_name='combo',
            name='membership',
            field=models.ManyToManyField(related_name='combos', to='gbe.Persona'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='is_teaching', to='gbe.Persona'),
        ),
        migrations.AddField(
            model_name='actbidevaluation',
            name='bid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.Act'),
        ),
        migrations.AddField(
            model_name='act',
            name='performer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='acts', to='gbe.Performer'),
        ),
        migrations.AddField(
            model_name='act',
            name='tech',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.TechInfo'),
        ),
        migrations.AlterUniqueTogether(
            name='volunteerinterest',
            unique_together=set([('interest', 'volunteer')]),
        ),
    ]
