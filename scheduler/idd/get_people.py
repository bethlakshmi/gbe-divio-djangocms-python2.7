from scheduler.models import PeopleAllocation
from scheduler.data_transfer import (
    Error,
    PeopleResponse,
    Person,
)
from django.db.models import Q


def get_people(parent_event_ids=[],
               event_ids=[],
               labels=[],
               label_sets=[],
               roles=[]):
    if len(labels) > 0 and len(label_sets) > 0:
        return PeopleResponse(
            errors=[Error(
                code="INVALID_REQUEST",
                details="labels and label_sets are not compatible"), ])
    people = []
    bookings = PeopleAllocation.objects.all()
    if len(labels) > 0:
        bookings = bookings.filter(event__eventlabel__text__in=labels)
    for label_set in label_sets:
        bookings = bookings.filter(event__eventlabel__text__in=label_set)
    if len(parent_event_ids) > 0:
        bookings = bookings.filter(
            Q(event__parent__pk__in=(parent_event_ids)) |
            Q(event__pk__in=parent_event_ids))
    if len(event_ids) > 0:
        bookings = bookings.filter(
            event__id__in=event_ids)
    if len(roles) > 0:
        bookings = bookings.filter(role__in=roles)
    for booking in bookings:
        person = Person(booking=booking)
        people += [person]

    return PeopleResponse(people=people)
