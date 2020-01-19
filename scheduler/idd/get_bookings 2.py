from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def get_bookings(occurrence_ids=[], roles=[], labels=[]):
    if len(occurrence_ids) == 0 and len(roles) == 0 and len(labels) == 0:
        response = PeopleResponse(
            errors=[Error(
                code="INVALID_REQUEST",
                details="Occurrence Ids, Roles and Labels are all blank, " +
                "at least 1 must be provided"), ])
    people = []
    bookings = ResourceAllocation.objects
    if len(occurrence_ids) > 0:
        bookings = bookings.filter(event__pk__in=occurrence_ids)
    if len(roles) > 0:
        bookings = bookings.filter(resource__worker__role__in=roles)
    if len(labels) > 0:
        bookings = bookings.filter(event__eventlabel__text__in=labels)
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
    return PeopleResponse(people=people)
