from scheduler.idd import get_occurrence
from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    PeopleResponse
)


def set_act(occurrence_id=None, act=None):
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
            return PeopleResponse(errors=[Error(
                code="BOOKING_NOT_FOUND",
                details="Booking id %s not found" % person.booking_id), ])
    else:
        return PeopleResponse(errors=[Error(
            code="OCCURRENCE_NOT_FOUND",
            details="Neither booking id nor occurrence id provided")])
    return occurrence.allocate_person(person)
