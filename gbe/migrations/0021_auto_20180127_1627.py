# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from gbe.models import (
    GenericEvent,
    StaffArea,
    Profile,
)
from scheduler.models import (
    Event,
    EventContainer,
    EventLabel,
    ResourceAllocation,
)
from django.utils.text import slugify


def move_staff_areas(apps, schema_editor):
    for event in GenericEvent.objects.filter(
            type="Staff Area",
            visible=True).order_by("e_conference", "e_title"):
        staff = StaffArea(
                conference=event.e_conference,
                title=event.e_title,
                description=event.e_description,
                slug=slugify(event.e_title))
        occurrence = Event.objects.filter(eventitem=event).first()
        if occurrence:
            staff.default_volunteers = occurrence.max_volunteer
            staff.default_location = occurrence.location.room
            booking = ResourceAllocation.objects.filter(
                event=occurrence,
                resource__worker__role="Staff Lead").first()
            if booking:
                staff.staff_lead = booking.resource.worker.workeritem
            else:
                print "no lead - %s" % str(occurrence)
        else:
            print "no occurrence - %s" % event.e_title
        staff.save()
        print "saved - %s" % event.e_title
        for container in EventContainer.objects.filter(
                parent_event__eventitem=event):
            label = EventLabel(event=container.child_event, text=staff.slug)
            label.save()
            print "set child - %s with slug %s" % (str(container.child_event),
                                                   staff.slug)

    # I'm not moving the stuff that isn't visible.  Not worth saving.
    GenericEvent.objects.filter(type="Staff Area").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0020_auto_20180127_0153'),
    ]

    operations = [
        migrations.RunPython(move_staff_areas),
    ]
