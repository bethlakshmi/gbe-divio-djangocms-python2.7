from scheduler.models import Event
from scheduler.data_transfer import (
    Error,
    Warning,
    GeneralResponse
)
from gbetext import parent_event_delete_warning


def delete_occurrences(connected_class, connected_id):
    response = GeneralResponse()
    delete_filter = Event.objects.filter(
        connected_class=connected_class,
        connected_id=connected_id)

    if Event.objects.filter(parent__in=delete_filter).exists():
        response.warnings = [Warning(
            code="PARENT_EVENT_DELETION",
            details=parent_event_delete_warning), ]

    if not delete_filter.exists():
        response.errors = [Error(
            code="OCCURRENCE_NOT_FOUND",
            details="Occurrence for %s with id %d not found" % (
                connected_class,
                connected_id)), ]
    else:
        delete_filter.delete()

    return response
