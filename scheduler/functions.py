from scheduler.models import (
    ResourceAllocation,
    Worker,
)


def get_scheduled_events_by_role(conference, roles):
    '''
    gets all the workeritems scheduled with a given set of roles for the
    given conference
    '''
    commits = ResourceAllocation.objects.filter(
        event__eventlabel__text=conference.conference_slug)
    workers = Worker.objects.filter(role__in=roles)
    return workers, commits
