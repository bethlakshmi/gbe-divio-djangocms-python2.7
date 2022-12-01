from scheduler.models import (
    Event,
    EventLabel,
)
from scheduler.data_transfer import OccurrenceResponse
from scheduler.idd import get_occurrence


def create_occurrence(title,
                      length,
                      event_style,
                      start_time,
                      max_volunteer=0,
                      max_commitments=0,
                      people=[],
                      locations=[],
                      description=None,
                      parent_event_id=None,
                      blurb=None,
                      labels=[],
                      approval=False,
                      slug=None,
                      connected_class="",
                      connected_id=None):
    if parent_event_id:
        parent_response = get_occurrence(parent_event_id)
        if parent_response.errors:
            return parent_response

    response = OccurrenceResponse()
    response.occurrence = Event(
        title=title,
        description=description,
        length=length,
        event_style=event_style,
        starttime=start_time,
        max_volunteer=max_volunteer,
        max_commitments=max_commitments,
        approval_needed=approval,
        slug=slug,
        connected_class=connected_class,
        connected_id=connected_id)

    if parent_event_id:
        response.occurrence.parent = parent_response.occurrence
    if blurb:
        response.occurrence.blurb = blurb

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
