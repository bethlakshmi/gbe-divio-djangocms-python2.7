from scheduler.models import (
    Event,
)
from scheduler.data_transfer import (
    Error,
    OccurrenceResponse
)


def get_occurrence(occurrence_id):
    response = None
    try:
        response = OccurrenceResponse(
            occurrence=Event.objects.get(pk=occurrence_id))
    except Event.DoesNotExist:
        response = OccurrenceResponse(
            errors=[Error(
                code="OCCURRENCE_NOT_FOUND",
                details="Occurrence id %s not found" % str(occurrence_id)), ])
    return response
