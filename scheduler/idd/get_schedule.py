from scheduler.data_transfer import (
    Error,
    ScheduleResponse,
    ScheduleItem,
)
from scheduler.models import PeopleAllocation
from gbetext import not_scheduled_roles


# DEPRECATE - not really deprecate, but totally rework when model
# refactor is done.  It bounces across apps hideously
def get_schedule(user=None,
                 labels=[],
                 start_time=None,
                 end_time=None,
                 roles=[],
                 commitment=None,
                 public_class=None,
                 public_id=None):
    basic_filter = PeopleAllocation.objects.all()
    sched_items = []
    if (public_class is None and public_id is not None) or (
            public_id is None and public_class is not None):
        return ScheduleResponse(errors=[Error(
            code="LINKED_CLASS_AND_ID_REQUIRED",
            details="Getting a schedule by class & id requires both items.")])

    if public_class is not None and public_id is not None and user is not None:
        return ScheduleResponse(errors=[Error(
            code="USER_AND_LINKED_CLASS_INCOMPATIBLE",
            details="User and Linked Class searching is incompatible.")])

    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)
    if end_time:
        basic_filter = basic_filter.filter(
            event__starttime__lt=end_time.replace(tzinfo=None))
    if commitment:
        basic_filter = basic_filter.filter(
            ordering__class_name=commitment.__class__.__name__,
            ordering__class_id=commitment.pk)

    if len(roles) > 0:
        basic_filter = basic_filter.filter(role__in=roles)
    else:
        basic_filter = basic_filter.exclude(role__in=not_scheduled_roles)

    if user:
        basic_filter = basic_filter.filter(people__users__in=[user])
    elif public_class and public_id:
        basic_filter = basic_filter.filter(people__class_name=public_class,
                                           people__class_id=public_id)

    for item in basic_filter:
        if (start_time and item.event.end_time >= start_time) or (
                start_time is None):

            order = None
            if hasattr(item, 'ordering'):
                order = item.ordering

            people_list = item.people.users.all()
            if user:
                people_list = item.people.users.filter(pk=user.pk)
            for list_user in people_list:
                sched_items += [ScheduleItem(
                    user=list_user,
                    event=item.event,
                    role=item.role,
                    label=item.label,
                    booking_id=item.pk,
                    commitment=order)]

    response = ScheduleResponse(
        schedule_items=sorted(
            set(sched_items),
            key=lambda sched_items: sched_items.event.start_time))
    return response
