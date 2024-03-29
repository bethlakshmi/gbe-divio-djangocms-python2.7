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
                      connected_id=None,
                      peer_id=None):
    if parent_event_id:
        parent_response = get_occurrence(parent_event_id)
        if parent_response.errors:
            parent_response.errors[0].code = "GET_PARENT_" + (
                parent_response.errors[0].code)
            return parent_response

    if peer_id:
        peer_response = get_occurrence(peer_id)
        if peer_response.errors:
            peer_response.errors[0].code = "GET_PEER_" + (
                peer_response.errors[0].code)
            return peer_response

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
    response.occurrence.save()
    if peer_id:
        response.occurrence.set_peer(peer_response.occurrence)

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
