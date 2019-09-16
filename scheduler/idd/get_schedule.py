from scheduler.data_transfer import (
    Error,
    ScheduleResponse,
    ScheduleItem,
)
from scheduler.models import ResourceAllocation


# DEPRECATE - not really deprecate, but totally rework when model
# refactor is done.  It bounces across apps hideously
def get_schedule(user=None,
                 labels=[],
                 start_time=None,
                 end_time=None,
                 roles=[]):
    basic_filter = ResourceAllocation.objects.all()
    sched_items = []
    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)
    if start_time:
        basic_filter = basic_filter.filter(
            event__starttime__gte=start_time)
    if end_time:
        basic_filter = basic_filter.filter(
            event__starttime__lt=end_time)
    if len(roles) > 0:
        basic_filter = basic_filter.filter(
            resource__worker__role__in=roles,
        )
    if user:
        bookable_items = user.profile.get_bookable_items()
        if len(bookable_items['acts']) > 0:
            for item in basic_filter.filter(
                    resource__actresource___item__in=bookable_items['acts']):
                booking_label = None
                if hasattr(item, 'label'):
                    booking_label = item.label
                sched_items += [ScheduleItem(
                    user=user,
                    event=item.event,
                    role="Performer",
                    label=booking_label)]
        if len(bookable_items['performers']) > 0:
            for item in basic_filter.filter(
                    resource__worker___item__in=bookable_items['performers']):
                booking_label = None
                if hasattr(item, 'label'):
                    booking_label = item.label
                sched_items += [ScheduleItem(
                    user=user,
                    event=item.event,
                    role=item.resource.as_subtype.role,
                    label=booking_label)]
        basic_filter = basic_filter.filter(
            resource__worker___item=user.profile)
    for item in basic_filter:
        resource = item.resource.as_subtype
        booking_label = None
        if hasattr(item, 'label'):
            booking_label = item.label
        if resource.__class__.__name__ == "Worker":
            sched_items += [ScheduleItem(
                user=resource.workeritem.user_object,
                event=item.event,
                role=resource.role,
                label=booking_label,
                booking_id=item.pk)]
        if resource.__class__.__name__ == "ActResource":
            for profile in resource._item.act.get_performer_profiles():
                sched_items += [ScheduleItem(
                    user=profile.user_object,
                    event=item.event,
                    role=resource.role or "Performing",
                    label=booking_label,
                    booking_id=item.pk)]
    response = ScheduleResponse(
        schedule_items=sorted(
            set(sched_items),
            key=lambda sched_items: sched_items.event.start_time))
    return response
