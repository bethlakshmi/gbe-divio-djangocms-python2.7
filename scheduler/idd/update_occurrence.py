from scheduler.models import (
    Event,
    EventLabel,
    PeopleAllocation,
)
from scheduler.data_transfer import OccurrenceResponse
from scheduler.idd import get_occurrence


def update_occurrence(occurrence_id,
                      title=None,
                      description=None,
                      start_time=None,
                      length=None,
                      max_volunteer=None,
                      max_commitments=None,
                      people=None,
                      roles=None,
                      locations=None,
                      approval=None,
                      parent_event_id=None,
                      labels=None,
                      slug=None):
    response = get_occurrence(occurrence_id)
    if response.errors:
        return response

    occurrence = response.occurrence
    if start_time:
        occurrence.starttime = start_time
    if max_volunteer is not None:
        occurrence.max_volunteer = max_volunteer
    if max_commitments is not None:
        occurrence.max_commitments = max_commitments
    if approval is not None:
        occurrence.approval_needed = approval
    if slug is not None:
        occurrence.slug = slug
    if title is not None:
        occurrence.title = title
    if description is not None:
        occurrence.description = description
    if length is not None:
        occurrence.length = length

    if parent_event_id is not None:
        if parent_event_id > -1:
            parent = get_occurrence(parent_event_id)
            if parent.errors:
                return parent
            occurrence.parent = parent.occurrence
        else:
            occurrence.parent = None

    if start_time or max_volunteer or approval or max_commitments or slug or (
            parent_event_id is not None):
        occurrence.save()

    if locations is not None:
        occurrence.set_locations(locations)

    if labels is not None:
        occurrence.eventlabel_set.all().delete()
        for label in labels:
            label = EventLabel(text=label, event=response.occurrence)
            label.save()

    warnings = []
    if people is not None:
        if roles is not None:
            PeopleAllocation.objects.filter(event=occurrence,
                                            role__in=roles).delete()
        else:
            PeopleAllocation.objects.filter(event=occurrence).delete()

        for person in people:
            warnings += occurrence.allocate_person(
                person).warnings
    response.warnings = warnings
    return response
