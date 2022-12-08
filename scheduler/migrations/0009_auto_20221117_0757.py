# Generated by Django 3.2.16 on 2022-11-17 07:57

from django.db import migrations


def migrate_event_inheritance(apps, schema_editor):
    schedEvent = apps.get_model("scheduler", "Event")
    ResourceAllocation = apps.get_model("scheduler", "ResourceAllocation")
    Location = apps.get_model("scheduler", "Location")
    gbeClass = apps.get_model("gbe", "Class")
    gbeShow = apps.get_model("gbe", "Show")
    gbeGeneric = apps.get_model("gbe", "GenericEvent")
    for event in schedEvent.objects.all():
        child = None
        # If it's a class...
        if gbeClass.objects.filter(
                eventitem_id=event.eventitem.eventitem_id).exists():
            child = gbeClass.objects.get(
                eventitem_id=event.eventitem.eventitem_id)
            # don't bother with un-accepted classes.
            if child.accepted != 3:
                print("not converted class %s" % (child.e_title))
                event.delete()
                continue
            # keep a pointer to the bid
            else:
                event.connected_id = child.pk
                event.connected_class = "Class"
                event.event_style = child.type

        # If it's a show....
        elif gbeShow.objects.filter(
                eventitem_id=event.eventitem.eventitem_id).exists():
            child = gbeShow.objects.get(
                eventitem_id=event.eventitem.eventitem_id)
            event.event_style = "Show"

        # If it's a GenericEvent...
        elif gbeGeneric.objects.filter(
                eventitem_id=event.eventitem.eventitem_id).exists():
            child = gbeGeneric.objects.get(
                eventitem_id=event.eventitem.eventitem_id)
            event.event_style = child.type

        else:
            print("Error!!! no child!!!???")
            continue

        # port all shows, generic events, and *accepted* classes
        event.title = child.e_title
        event.description = child.e_description
        event.blurb = child.blurb
        event.length = child.duration
        if child.default_location:
            # make resource alloc with "default" location
            if Location.objects.filter(
                    _item__pk=child.default_location.pk).exists():
                loc = Location.objects.get(_item__pk=child.default_location.pk)
                print("found location %s" % child.default_location.name)
            else:
                loc = Location(_item=child.default_location)
                loc.save()
                print("made location %s" % child.default_location.name)
            booking = ResourceAllocation(
                default=True,
                event=event,
                resource=loc)
            booking.save()
            print("made default room %s for %s" % (
                child.default_location.name,
                event.title))

        event.save()


def reverse_event_inheritance(apps, schema_editor):
    schedEvent = apps.get_model("scheduler", "Event")
    Location = apps.get_model("scheduler", "Location")
    Room = apps.get_model("gbe", "Room")
    gbeClass = apps.get_model("gbe", "Class")
    gbeShow = apps.get_model("gbe", "Show")
    gbeGeneric = apps.get_model("gbe", "GenericEvent")
    for event in schedEvent.objects.all():
        if event.connected_class == "Class":
            gbe_event = gbeClass.objects.get(pk=event.connected_id)
        elif event.event_style == "Show":
            gbe_event = gbeShow()
        else:
            gbe_event = gbeGeneric(type=event.event_style)
        gbe_event.e_title = event.title
        gbe_event.e_description = event.description
        gbe_event.blurb = event.blurb
        gbe_event.duration = event.length
        if event.resources_allocated.filter(default=True).exists:
            for alloc in event.resources_allocated.filter(default=True):
                if Location.objects.filter(pk=alloc.resource.pk).exists():
                    loc = Location.objects.get(pk=alloc.resource.pk)
                    room = Room.objects.get(pk=loc._item.pk)
                    gbe_event.default_room = room
                    print("set default room %s for event %s" % (
                        gbe_event.default_room.name,
                        gbe_event.e_title))
        gbe_event.save()
        event.eventitem = gbe_event
        event.save()


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0008_auto_20221117_0756'),
        ('gbe', '0020_alter_profile_phone')
    ]

    operations = [
        migrations.RunPython(migrate_event_inheritance,
                             reverse_code=reverse_event_inheritance)
    ]
