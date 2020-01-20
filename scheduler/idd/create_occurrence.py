from scheduler.models import (
    Event,
    EventContainer,
    EventItem,
    EventLabel,
)
from scheduler.data_transfer import OccurrenceResponse
from scheduler.idd import get_occurrence


def create_occurrence(foreign_event_id,
                      start_time,
                      max_volunteer=0,
                      people=[],
                      locations=[],
                      parent_event_id=None,
                      labels=[],
                      approval=False):
    if parent_event_id:
        parent_response = get_occurrence(parent_event_id)
        if parent_response.errors:
            return parent_response

    response = OccurrenceResponse()
    response.occurrence = Event(
        eventitem=EventItem.objects.get(eventitem_id=foreign_event_id),
        starttime=start_time,
        max_volunteer=max_volunteer,
        approval_needed=approval)
    response.occurrence.save()
    if len(locations) > 0:
        response.occurrence.set_locations(locations)

    for person in people:
        response.warnings += response.occurrence.allocate_person(
            person).warnings

    for label in labels:
        response.occurrence.add_label(label)

    if parent_event_id:
        family = EventContainer(
            parent_event=parent_response.occurrence,
            child_event=response.occurrence)
        family.save()

    return response
