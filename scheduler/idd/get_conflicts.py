from scheduler.data_transfer import (
    Error,
    OccurrencesResponse,
)
from scheduler.idd import get_occurrence
from scheduler.models import ResourceAllocation


# assumes that start time is already before end time,
def check_conflict(occurrence, potential_conflict):
    is_conflict = False
    if potential_conflict.start_time >= occurrence.start_time:
        is_conflict = True
    elif potential_conflict.end_time > occurrence.start_time:
        is_conflict = True
    return is_conflict


# DEPRECATE - not really deprecate, but totally rework when model
# refactor is done.  It bounces across apps hideously
def get_conflicts(conflict_occurrence_id,
                  user=None,
                  labels=[]):
    response = get_occurrence(conflict_occurrence_id)
    if len(response.errors) > 0:
        return response
    basic_filter = ResourceAllocation.objects.filter(
        event__starttime__lt=response.occurrence.end_time)
    sched_items = []
    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)
    if user:
        bookable_items = user.profile.get_bookable_items()
        if len(bookable_items['acts']) > 0:
            for item in basic_filter.filter(
                    resource__actresource___item__in=bookable_items['acts']):
                if check_conflict(response.occurrence, item.event) and (
                        item.event not in sched_items):
                    sched_items += [item.event]
        if len(bookable_items['performers']) > 0:
            for item in basic_filter.filter(
                    resource__worker___item__in=bookable_items['performers']):
                if check_conflict(response.occurrence, item.event) and (
                        item.event not in sched_items):
                    sched_items += [item.event]
        basic_filter = basic_filter.filter(
            resource__worker___item=user.profile)
    for item in basic_filter:
        if check_conflict(response.occurrence, item.event) and (
                item.event not in sched_items):
            sched_items += [item.event]

    response = OccurrencesResponse(
        occurrences=sorted(
            set(sched_items),
            key=lambda sched_items: sched_items.start_time))
    return response
