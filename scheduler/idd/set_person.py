from scheduler.idd import get_occurrence
from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    BookingResponse
)


def set_person(occurrence_id=None, person=None):
    occurrence = None
    alloc = None
    if occurrence_id:
        occ_response = get_occurrence(occurrence_id)
        if occ_response.errors:
            return occ_response
        occurrence = occ_response.occurrence
    elif person and person.booking_id:
        try:
            alloc = ResourceAllocation.objects.get(pk=person.booking_id)
            occurrence = alloc.event
        except ResourceAllocation.DoesNotExist:
            return BookingResponse(errors=[Error(
                code="BOOKING_NOT_FOUND",
                details="Booking id %s not found" % person.booking_id), ])
    else:
        return BookingResponse(errors=[Error(
            code="OCCURRENCE_NOT_FOUND",
            details="Neither booking id nor occurrence id provided")])
    if person.booking_id and not ResourceAllocation.objects.filter(
            pk=person.booking_id).exists():
        return BookingResponse(errors=[Error(
                code="BOOKING_NOT_FOUND",
                details="Booking id %s not found" % person.booking_id), ])
    return occurrence.allocate_person(person)
