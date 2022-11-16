from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)
from django.db.models import Q


def get_all_container_bookings(occurrence_ids, roles=[]):
    people = []
    bookings = ResourceAllocation.objects.filter(
        Q(event__pk__in=occurrence_ids) |
        Q(event__parent__pk__in=occurrence_ids)
        ).distinct()
    if len(roles) > 0:
        bookings = bookings.filter(resource__worker__role__in=roles)
    for booking in bookings:
        if booking.resource.as_subtype.__class__.__name__ == "Worker":
            person = Person(booking=booking)
            if hasattr(booking, 'label'):
                person.label = booking.label.text
            people += [person]
    return PeopleResponse(people=people)
