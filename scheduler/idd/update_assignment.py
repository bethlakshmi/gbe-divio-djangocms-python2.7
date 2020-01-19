from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    AssignmentsResponse,
    Assignment,
)


def update_assignment(booking_id, role=None):
    response = AssignmentsResponse()
    try:
        booking = ResourceAllocation.objects.get(pk=booking_id)
    except ResourceAllocation.DoesNotExist:
        response.errors = [Error(
            code="BOOKING_NOT_FOUND",
            details="Could not find booking id %d for occurrence id %d." % (
                booking_id, occurrence_id))]
        return response
    if role:
        booking.resource.worker.role = role
        booking.resource.worker.save()
    return AssignmentsResponse(assignments=[Assignment(booking=booking)])
