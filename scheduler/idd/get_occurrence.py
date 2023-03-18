from scheduler.models import (
    Event,
)
from scheduler.data_transfer import (
    Error,
    OccurrenceResponse
)


def get_occurrence(occurrence_id=None, booking_id=None):
    response = None
    try:
        if occurrence_id is not None:
            response = OccurrenceResponse(
                occurrence=Event.objects.get(pk=occurrence_id))
        else:
            response = OccurrenceResponse(
                occurrence=Event.objects.get(
                    resources_allocated__pk=booking_id))            
    except Event.DoesNotExist:
        response = OccurrenceResponse(
            errors=[Error(
                code="OCCURRENCE_NOT_FOUND",
                details="Occurrence id %s not found" % str(occurrence_id)), ])
    return response
