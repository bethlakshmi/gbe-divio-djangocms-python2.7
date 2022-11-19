from scheduler.models import (
    Event,
)
from scheduler.data_transfer import (
    Error,
    OccurrencesResponse
)
from datetime import (
    datetime,
    time
)


def get_occurrences(parent_event_id=None,
                    labels=[],
                    label_sets=[],
                    event_styles=[],
                    day=None,
                    max_volunteer=None):
    if len(labels) > 0 and len(label_sets) > 0:
        return OccurrencesResponse(
            errors=[Error(
                code="INVALID_REQUEST",
                details="labels and label_sets are not compatible"), ])
    response = OccurrencesResponse()
    filter_occurrences = Event.objects.all()

    if parent_event_id:
        filter_occurrences = filter_occurrences.filter(
            parent__pk=parent_event_id)
    for label in labels:
        filter_occurrences = filter_occurrences.filter(
            eventlabel__text=label
        )
    for label_set in label_sets:
        filter_occurrences = filter_occurrences.filter(
            eventlabel__text__in=label_set
        )
    if max_volunteer is not None:
        filter_occurrences = filter_occurrences.filter(
            max_volunteer__gte=max_volunteer)
    if len(event_styles) > 0:
        filter_occurrences = filter_occurrences.filter(
            event_style__in=event_styles)
    if day:
        filter_occurrences = filter_occurrences.filter(
            starttime__range=(
                datetime.combine(day, time(0, 0, 0, 0)),
                datetime.combine(day, time(23, 59, 59, 999999)))
        )

    response.occurrences = filter_occurrences.order_by('starttime')
    return response
