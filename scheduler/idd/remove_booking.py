from scheduler.idd import test_booking
from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    PersonResponse,
)


def remove_booking(occurrence_id,
                   booking_id):
    response = PersonResponse()
    test = test_booking(booking_id, occurrence_id)
    if not test:
        response.errors = [Error(
            code="BOOKING_NOT_FOUND",
            details="Could not find booking id %d for occurrence id %d." % (
                booking_id, occurrence_id))]
        return response
    ResourceAllocation.objects.filter(pk=booking_id).delete()
    response.booking_id = booking_id
    return response
