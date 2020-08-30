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
                      approval=None):
    response = get_occurrence(occurrence_id)
    if response.errors:
        return response

    if start_time:
        response.occurrence.starttime = start_time
    if max_volunteer is not None:
        response.occurrence.max_volunteer = max_volunteer
    if max_commitments is not None:
        response.occurrence.max_commitments = max_commitments
    if approval is not None:
        response.occurrence.approval_needed = approval
    if start_time or max_volunteer or approval or max_commitments:
        response.occurrence.save()

    if locations is not None:
        response.occurrence.set_locations(locations)

    warnings = []
    if people is not None:
        if roles == "All":
            Worker.objects.filter(
                allocations__event=response.occurrence).delete()
        else:
            Worker.objects.filter(allocations__event=response.occurrence,
                                  role__in=roles).delete()
        for person in people:
            warnings += response.occurrence.allocate_person(
                person).warnings
    response.warnings = warnings
    return response
