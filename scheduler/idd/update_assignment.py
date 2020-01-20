from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    AssignmentsResponse,
    Assignment,
    Warning,
)
from scheduler.idd import get_conflicts


def update_assignment(booking_id, role=None, check_conflicts=False):
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
    response.assignments = [Assignment(booking=booking)]
    if check_conflicts:
        warnings = []
        conflicts = get_conflicts(
            response.assignments[0].occurrence.pk,
            response.assignments[0].person.user)
        for occurrence in conflicts.occurrences:
            warnings += [Warning(
                code="SCHEDULE_CONFLICT",
                user=response.assignments[0].person.user,
                occurrence=occurrence)]
        if len(warnings) > 0:
            response.warnings = warnings
    return response
