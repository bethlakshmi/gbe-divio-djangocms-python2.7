from scheduler.idd import get_occurrence
from scheduler.models import PeopleAllocation
from scheduler.data_transfer import (
    Error,
    BookingResponse
)


def set_person(occurrence_id=None, person=None):

    # - sets the specified occurrence or booking to the person details defined
    # - occurrence id takes precedence over booking id
    # - sets the occurrence's peer to that person - if a booking exists for
    #   the peer and person, that booking is changed as defined in this person

    occurrence = None
    alloc = None
    orig_person = None
    if occurrence_id:
        occ_response = get_occurrence(occurrence_id)
        if occ_response.errors:
            return occ_response
        occurrence = occ_response.occurrence
    elif person and person.booking_id:
        try:
            alloc = PeopleAllocation.objects.get(pk=person.booking_id)
            occurrence = alloc.event
        except PeopleAllocation.DoesNotExist:
            return BookingResponse(errors=[Error(
                code="BOOKING_NOT_FOUND",
                details="Booking id %s not found" % person.booking_id), ])
    else:
        return BookingResponse(errors=[Error(
            code="OCCURRENCE_NOT_FOUND",
            details="Neither booking id nor occurrence id provided")])
    if person.booking_id and not PeopleAllocation.objects.filter(
            pk=person.booking_id).exists():
        return BookingResponse(errors=[Error(
                code="BOOKING_NOT_FOUND",
                details="Booking id %s not found" % person.booking_id), ])
    elif person.booking_id and occurrence.peer is not None:
        orig_person = PeopleAllocation.objects.get(pk=person.booking_id).people

    response = occurrence.allocate_person(person)
    if occurrence.peer is not None:
        if orig_person is not None and PeopleAllocation.objects.filter(
                event__peer__pk=occurrence.pk,
                people=orig_person):
            #  Assumption - there is only 1 because pairs are exclusive
            peer_booking = PeopleAllocation.objects.filter(
                event__peer__pk=occurrence.pk,
                people=orig_person).first()
            person.booking_id = peer_booking.pk
        else:
            person.booking_id = None
        peer_response = occurrence.peer.allocate_person(person)
        response.booking_ids = response.booking_ids + peer_response.booking_ids
        response.occurrences += [occurrence.peer]
        response.warnings = response.warnings + peer_response.warnings
        response.errors = response.errors + peer_response.errors

    return response
