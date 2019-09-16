from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    GeneralResponse,
)


def remove_person(user, labels=[], roles=[]):
    basic_filter = ResourceAllocation.objects.all()
    sched_items = []
    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)
    if len(roles) > 0:
        basic_filter = basic_filter.filter(
            resource__worker__role__in=roles,
        )
    basic_filter.filter(
        resource__worker___item__in=user.profile.personae.all()).delete()

    basic_filter.filter(
        resource__worker___item=user.profile).delete()

    return GeneralResponse()
