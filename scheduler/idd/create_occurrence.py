from scheduler.models import (
    Event,
    EventItem,
    EventLabel,
)
from scheduler.data_transfer import OccurrenceResponse
from scheduler.idd import get_occurrence


def create_occurrence(foreign_event_id,
                      start_time,
                      max_volunteer=0,
                      max_commitments=0,
                      people=[],
                      locations=[],
                      parent_event_id=None,
                      labels=[],
                      approval=False,
                      slug=None):
    if parent_event_id:
        parent_response = get_occurrence(parent_event_id)
        if parent_response.errors:
            return parent_response

    response = OccurrenceResponse()
    response.occurrence = Event(
        eventitem=EventItem.objects.get(eventitem_id=foreign_event_id),
        starttime=start_time,
        max_volunteer=max_volunteer,
        max_commitments=max_commitments,
        approval_needed=approval,
        slug=slug)

    if parent_event_id:
        response.occurrence.parent = parent_response.occurrence

    response.occurrence.save()

    if len(locations) > 0:
        response.occurrence.set_locations(locations)

    for person in people:
        response.warnings += response.occurrence.allocate_person(
            person).warnings

    for label in labels:
        label = EventLabel(text=label, event=response.occurrence)
        label.save()

    return response
