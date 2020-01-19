from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Assignment,
    AssignmentsResponse,
)


def get_assignments(roles=[], labels=[]):
    if len(roles) == 0 and len(labels) == 0:
        response = AssignmentsResponse(
            errors=[Error(
                code="INVALID_REQUEST",
                details="Occurrence Ids, Roles and Labels are all blank, " +
                "at least 1 must be provided"), ])
    assignments = []
    bookings = ResourceAllocation.objects
    if len(roles) > 0:
        bookings = bookings.filter(resource__worker__role__in=roles)
    if len(labels) > 0:
        bookings = bookings.filter(event__eventlabel__text__in=labels)
    for booking in bookings:
        if booking.resource.as_subtype.__class__.__name__ == "Worker":
            assignments += [Assignment(booking=booking)]
    return AssignmentsResponse(assignments=assignments)
