from scheduler.models import Event
from scheduler.data_transfer import (
    Error,
    Warning,
    GeneralResponse
)
from gbetext import parent_event_delete_warning


def delete_occurrence(occurrence_id):
    response = GeneralResponse()
    if Event.objects.filter(parent__pk=occurrence_id).exists():
        response.warnings = [Warning(
            code="PARENT_EVENT_DELETION",
            details=parent_event_delete_warning), ]

    if not Event.objects.filter(pk=occurrence_id).exists():
        response.errors = [Error(
            code="OCCURRENCE_NOT_FOUND",
            details="Occurrence id %d not found" % occurrence_id), ]
    else:
        Event.objects.filter(pk=occurrence_id).delete()

    return response
