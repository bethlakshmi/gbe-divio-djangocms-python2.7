# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from gbetext import calendar_for_event


def create_labels(apps, schema_editor):
    Event = apps.get_model('scheduler', 'Event')
    EventItem = apps.get_model('scheduler', 'EventItem')
    Class = apps.get_model('gbe', 'Class')
    Show = apps.get_model('gbe', 'Show')
    GenericEvent = apps.get_model('gbe', 'GenericEvent')
    EventLabel = apps.get_model('scheduler', 'EventLabel')
    for event in Event.objects.all():
        try:
            gbe_event = Class.objects.get(eventitem_id=event.eventitem.eventitem_id)
        except:
            try:
                gbe_event = Show.objects.get(pk=event.eventitem.event.pk)
            except:
                try:
                    gbe_event = GenericEvent.objects.get(pk=event.eventitem.event.pk)
                except:
                    raise Exception(
                        "can't find: %s, %d" % (
                            event.eventitem.event.e_title, event.eventitem.eventitem_id))
        label = EventLabel(
            text=event.eventitem.event.e_conference.conference_slug,
            event=event)
        label.save()
        if gbe_event.__class__.__name__ == "GenericEvent":
            label_text = calendar_for_event[gbe_event.type]
        else:
            label_text = calendar_for_event[gbe_event.__class__.__name__]
        if label_text:
            label = EventLabel(
                text=label_text,
                event=event)
            label.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0003_eventlabel'),
    ]

    operations = [
        migrations.RunPython(create_labels),
    ]
