from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def get_bookings(occurrence_ids, roles=[]):
    people = []
    bookings = ResourceAllocation.objects.filter(event__pk__in=occurrence_ids)
    if len(roles) > 0:
        bookings = bookings.filter(resource__worker__role__in=roles)
    for booking in bookings:
        if booking.resource.as_subtype.__class__.__name__ == "Worker":
            person = Person(booking=booking)
            if hasattr(booking, 'label'):
                person.label = booking.label.text
            people += [person]
    return PeopleResponse(people=people)
