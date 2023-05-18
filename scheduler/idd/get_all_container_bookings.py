from scheduler.models import PeopleAllocation
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)
from django.db.models import Q


def get_all_container_bookings(occurrence_ids, roles=[]):
    people = []
    bookings = PeopleAllocation.objects.filter(
        Q(event__pk__in=occurrence_ids) |
        Q(event__children__pk__in=occurrence_ids)
        ).distinct()
    if len(roles) > 0:
        bookings = bookings.filter(role__in=roles)
    for booking in bookings:
        people += [Person(booking=booking)]
    return PeopleResponse(people=people)
