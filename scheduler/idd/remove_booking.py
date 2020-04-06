from scheduler.idd import test_booking
from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    BookingResponse,
)


def remove_booking(occurrence_id,
                   booking_id):
    response = BookingResponse()
    test = test_booking(booking_id, occurrence_id)
    if not test:
        response.errors = [Error(
            code="BOOKING_NOT_FOUND",
            details="Could not find booking id %d for occurrence id %d." % (
                booking_id, occurrence_id))]
        return response
    deleteable_resources = []
    bookings = ResourceAllocation.objects.filter(pk=booking_id)
    for booking in bookings:
        if booking.resource.allocations.count() == 1:
            deleteable_resources += [booking.resource]
    bookings.delete()
    for resource in deleteable_resources:
        resource.delete()
    response.booking_id = booking_id
    return response
