from scheduler.models import (
    Event,
    EventContainer,
    EventLabel,
    Worker,
)
from scheduler.data_transfer import OccurrenceResponse
from scheduler.idd import get_occurrence


def update_occurrence(occurrence_id,
                      start_time=None,
                      max_volunteer=None,
                      max_commitments=None,
                      people=None,
                      roles="All",
                      locations=None,
                      approval=None,
                      parent_event_id=None,
                      labels=None):
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
    if start_time or max_volunteer or approval or max_commitments:
        occurrence.save()
    if locations is not None:
        occurrence.set_locations(locations)
    if parent_event_id is not None:
        if hasattr(occurrence, 'container_event'):
            occurrence.container_event.delete()
        if parent_event_id > -1:
            parent = get_occurrence(parent_event_id)
            if parent.errors:
                return parent
            family = EventContainer(
                child_event=response.occurrence,
                parent_event=parent.occurrence)
            family.save()
    if labels is not None:
        occurrence.eventlabel_set.all().delete()
        for label in labels:
            label = EventLabel(text=label, event=response.occurrence)
            label.save()

    warnings = []
    if people is not None:
        if roles == "All":
            Worker.objects.filter(
                allocations__event=occurrence).delete()
        else:
            Worker.objects.filter(allocations__event=occurrence,
                                  role__in=roles).delete()
        for person in people:
            warnings += occurrence.allocate_person(
                person).warnings
    response.warnings = warnings
    return response
