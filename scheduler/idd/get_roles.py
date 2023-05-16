from scheduler.data_transfer import (
    Error,
    RolesResponse,
)
from scheduler.models import PeopleAllocation


def get_roles(user,
              labels=[]):
    roles = []
    basic_filter = PeopleAllocation.objects.filter(people__users__in=[user])
    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)

    for item in basic_filter:
        if item.role not in roles:
            roles += [item.role]

    response = RolesResponse(roles=sorted(roles))
    return response
