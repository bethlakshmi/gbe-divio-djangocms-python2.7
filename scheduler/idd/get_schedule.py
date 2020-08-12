from scheduler.data_transfer import (
    Error,
    ScheduleResponse,
    ScheduleItem,
)
from scheduler.models import ResourceAllocation
from gbetext import not_scheduled_roles


# DEPRECATE - not really deprecate, but totally rework when model
# refactor is done.  It bounces across apps hideously
def get_schedule(user=None,
                 labels=[],
                 start_time=None,
                 end_time=None,
                 roles=[],
                 commitment=None):
    basic_filter = ResourceAllocation.objects.all()
    sched_items = []

    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)
    if end_time:
        basic_filter = basic_filter.filter(
            event__starttime__lte=end_time.replace(tzinfo=None))
    if commitment:
        basic_filter = basic_filter.filter(
            ordering__class_name=commitment.__class__.__name__,
            ordering__class_id=commitment.pk)

    if len(roles) > 0:
        worker_filter = basic_filter.filter(
            resource__worker__role__in=roles,
        )
    else:
        worker_filter = basic_filter.exclude(
            resource__worker__role__in=not_scheduled_roles)
    if user:
        bookable_items = user.profile.get_bookable_items()
        if len(bookable_items['performers']) > 0:
            for item in worker_filter.filter(
                    resource__worker___item__in=bookable_items['performers']):
                booking_label = None
                order = None
                if hasattr(item, 'ordering'):
                    order = item.ordering
                if hasattr(item, 'label'):
                    booking_label = item.label
                if (start_time and item.event.end_time >= start_time) or (
                        start_time is None):
                    sched_items += [ScheduleItem(
                        user=user,
                        event=item.event,
                        role=item.resource.as_subtype.role,
                        label=booking_label,
                        order=order)]
        worker_filter = worker_filter.filter(
            resource__worker___item=user.profile)

    for item in worker_filter:
        if (start_time and item.event.end_time >= start_time) or (
                start_time is None):
            resource = item.resource.as_subtype
            booking_label = None
            if hasattr(item, 'label'):
                booking_label = item.label
            if resource.__class__.__name__ == "Worker":
                order = None
                if hasattr(item, 'ordering'):
                    order = item.ordering
                sched_items += [ScheduleItem(
                    user=resource.workeritem.user_object,
                    event=item.event,
                    role=resource.role,
                    label=booking_label,
                    booking_id=item.pk,
                    order=order)]                    
    response = ScheduleResponse(
        schedule_items=sorted(
            set(sched_items),
            key=lambda sched_items: sched_items.event.start_time))
    return response
