from scheduler.models import Event
from scheduler.data_transfer import (
    Error,
    Warning,
    GeneralResponse
)
from gbetext import parent_event_delete_warning


def delete_occurrence(occurrence_id):
    response = GeneralResponse()
    if not Event.objects.filter(pk=occurrence_id).exists():
        response.errors = [Error(
            code="OCCURRENCE_NOT_FOUND",
            details="Occurrence id %d not found" % occurrence_id), ]

    event = Event.objects.get(pk=occurrence_id)
    if event.children.exists():
        response.warnings = [Warning(
            code="PARENT_EVENT_DELETION",
            details=parent_event_delete_warning), ]
    event.delete()

    return response
