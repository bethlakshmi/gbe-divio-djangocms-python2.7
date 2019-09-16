from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    PeopleResponse,
    Person,
)
from django.db.models import Q


def get_people(parent_event_ids=[], labels=[], label_sets=[], roles=[]):
    if len(labels) > 0 and len(label_sets) > 0:
        return PeopleResponse(
            errors=[Error(
                code="INVALID_REQUEST",
                details="labels and label_sets are not compatible"), ])
    people = []
    bookings = ResourceAllocation.objects.all()
    act_bookings = []
    if len(labels) > 0:
        bookings = bookings.filter(event__eventlabel__text__in=labels)
    for label_set in label_sets:
        bookings = bookings.filter(event__eventlabel__text__in=label_set)
    if len(parent_event_ids) > 0:
        bookings = bookings.filter(Q(
            event__container_event__parent_event__eventitem__eventitem_id__in=(
                parent_event_ids)) |
            Q(event__eventitem__eventitem_id__in=parent_event_ids))
    if "Performer" in roles:
        act_bookings = bookings.filter(resource__actresource__pk__gt=0)
    if len(roles) > 0:
        bookings = bookings.filter(resource__worker__role__in=roles)
    for booking in bookings:
        if booking.resource.as_subtype.__class__.__name__ == "Worker":
            person = Person(
                booking_id=booking.pk,
                worker=booking.resource.worker,
                role=booking.resource.worker.role,
                )
            if hasattr(booking, 'label'):
                person.label = booking.label.text
            people += [person]
    for booking in act_bookings:
        if booking.resource.as_subtype.__class__.__name__ == "ActResource":
            performer = booking.resource.actresource.item.as_subtype.performer
            person = Person(
                booking_id=booking.pk,
                user=performer.user_object,
                role="Performer",
                public_class=performer.__class__.__name__,
                public_id=performer.pk
                )
            if hasattr(booking, 'label'):
                person.label = booking.label.text
            people += [person]
    return PeopleResponse(people=people)
