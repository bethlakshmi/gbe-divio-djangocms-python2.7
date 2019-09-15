from scheduler.data_transfer import (
    Error,
    RolesResponse,
)
from scheduler.models import ResourceAllocation


# DEPRECATE - not really deprecate, but totally rework when model
# refactor is done.  It bounces across apps hideously
def get_roles(user,
              labels=[]):
    roles = []
    basic_filter = ResourceAllocation.objects.all()
    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)
    bookable_items = user.profile.get_bookable_items()
    if len(bookable_items['acts']) > 0:
        if basic_filter.filter(
                resource__actresource___item__in=bookable_items['acts']
                ).exists():
            roles = ["Performer"]

    worker_items = bookable_items['performers']
    worker_items += [user.profile]
    resources = basic_filter.filter(
        resource__worker___item__in=worker_items
        )
    for item in resources:
        if item.resource.as_subtype.role not in roles:
            roles += [item.resource.as_subtype.role]

    response = RolesResponse(roles=sorted(roles))
    return response
