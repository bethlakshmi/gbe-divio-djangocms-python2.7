from tests.factories.scheduler_factories import (
    EventLabelFactory,
    PeopleFactory,
    PeopleAllocationFactory,
    SchedEventFactory,
)
from scheduler.models import People
from tests.factories.gbe_factories import ConferenceFactory
from gbetext import calendar_for_event
from datetime import (
    datetime,
    time
)


def book_worker_item_for_role(public_class, role, conference=None):
    people = None
    if public_class.__class__.__name__ == "Bio":
        people = get_or_create_bio(public_class)
    else:
        people = get_or_create_profile(public_class)

    event = SchedEventFactory()

    if conference is not None:
        EventLabelFactory(
            event=event,
            text=conference.conference_slug
        )
    else:
        EventLabelFactory(
            event=event,
            text=ConferenceFactory().conference_slug
        )
    EventLabelFactory(
        event=event,
        text=calendar_for_event[event.event_style]
    )
    booking = PeopleAllocationFactory(
        event=event,
        people=people,
        role=role
    )
    return booking


def noon(day):
    return datetime.combine(day.day,
                            time(12, 0, 0))


def get_or_create_bio(public_class,
                      commitment_class_name="",
                      commitment_class_id=None):
    people = None
    if not People.objects.filter(
            class_name=public_class.__class__.__name__,
            class_id=public_class.pk,
            commitment_class_name=commitment_class_name,
            commitment_class_id=commitment_class_id).exists():
        people = People(class_name=public_class.__class__.__name__,
                        class_id=public_class.pk,
                        commitment_class_name=commitment_class_name,
                        commitment_class_id=commitment_class_id)
        people.save()
        people.users.add(public_class.contact.user_object)
    else:
        people = People.objects.get(
            class_name=public_class.__class__.__name__,
            class_id=public_class.pk,
            commitment_class_name=commitment_class_name,
            commitment_class_id=commitment_class_id)
    return people


def get_or_create_profile(public_class):
    people = None
    if not People.objects.filter(
            class_name=public_class.__class__.__name__,
            class_id=public_class.pk).exists():
        people = People(class_name=public_class.__class__.__name__,
                        class_id=public_class.pk)
        people.save()
        people.users.add(public_class.user_object)
    else:
        people = People.objects.get(
            class_name=public_class.__class__.__name__,
            class_id=public_class.pk)
    return people
