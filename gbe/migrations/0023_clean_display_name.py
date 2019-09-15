# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.db import migrations, models


def clean_display_name(apps, schema_editor):
    Profile = apps.get_model('gbe', 'Profile')
    for profile in Profile.objects.all():
        if profile.display_name != profile.display_name.strip():
            profile.display_name = profile.display_name.strip()
            profile.save()
            print "trimmed: " + profile.display_name
        if profile.display_name != re.sub(' +', ' ', profile.display_name):
            profile.display_name = re.sub(' +', ' ', profile.display_name)
            profile.save()
            print "removed whitespace: " + profile.display_name
        if profile.display_name != profile.display_name.title():
            profile.display_name = profile.display_name.title()
            profile.save()
            print "title case: " + profile.display_name


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0022_auto_20180129_0159'),
    ]

    operations = [
        migrations.RunPython(clean_display_name),
    ]
