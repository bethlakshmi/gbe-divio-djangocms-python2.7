from scheduler.idd import test_booking
from scheduler.models import PeopleAllocation
from scheduler.data_transfer import (
    Error,
    BookingResponse,
)


def remove_booking(occurrence_id,
                   booking_id):
    # removes this booking from this occurrence
    # also removes the people set in that booking from any peered events
    response = BookingResponse()
    test = test_booking(booking_id, occurrence_id)
    if not test:
        response.errors = [Error(
            code="BOOKING_NOT_FOUND",
            details="Could not find booking id %d for occurrence id %d." % (
                booking_id, occurrence_id))]
        return response
    booking = PeopleAllocation.objects.get(pk=booking_id)
    people = booking.people
    event = booking.event
    booking.delete()
    response = BookingResponse(booking_id=booking_id,
                               occurrence=event)

    for alloc in PeopleAllocation.objects.filter(
            event__peer__pk=occurrence_id,
            people=people):
        response.booking_ids += [alloc.pk]
        response.occurrences += [alloc.event]
        alloc.delete()

    return response
