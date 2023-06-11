from scheduler.idd import test_booking
from scheduler.models import PeopleAllocation
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
    bookings = PeopleAllocation.objects.filter(pk=booking_id)
    bookings.delete()
    response.booking_id = booking_id
    return response
