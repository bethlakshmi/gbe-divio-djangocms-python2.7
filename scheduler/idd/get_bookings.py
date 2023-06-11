from scheduler.models import PeopleAllocation
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def get_bookings(occurrence_ids, roles=[]):
    people = []
    bookings = PeopleAllocation.objects.filter(event__pk__in=occurrence_ids)
    if len(roles) > 0:
        bookings = bookings.filter(role__in=roles)
    for booking in bookings:
        people += [Person(booking=booking)]
    return PeopleResponse(people=people)
