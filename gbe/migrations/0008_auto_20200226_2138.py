# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-26 21:38
from __future__ import unicode_literals

from django.db import migrations


def centralize_techinfo(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    TechInfo = apps.get_model('gbe', 'TechInfo')
    for techinfo in TechInfo.objects.all():
        techinfo.track_title = techinfo.audio.track_title
        techinfo.track_artist = techinfo.audio.track_artist
        techinfo.duration = techinfo.stage.act_duration
        techinfo.feel_of_act = techinfo.lighting.notes
        techinfo.introduction_text = techinfo.stage.intro_text
        techinfo.crew_instruct = techinfo.stage.notes
        techinfo.save()


def decentralize_techinfo(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    TechInfo = apps.get_model('gbe', 'TechInfo')
    for techinfo in TechInfo.objects.all():
        techinfo.audio.track_title = techinfo.track_title
        techinfo.audio.track_artist = techinfo.track_artist
        techinfo.stage.act_duration = techinfo.duration
        techinfo.lighting.notes = techinfo.feel_of_act
        techinfo.stage.intro_text = techinfo.introduction_text
        techinfo.stage.notes = techinfo.crew_instruct
        techinfo.audio.save()
        techinfo.stage.save()
        techinfo.lighting.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0007_auto_20200224_2046'),
    ]

    operations = [
        migrations.RunPython(centralize_techinfo, decentralize_techinfo),
    ]
