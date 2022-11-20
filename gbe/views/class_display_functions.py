from django.urls import reverse
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
)
from gbe.models import Class


def get_bid_and_scheduling_info(bid_class, bid_id):
    if bid_class != 'Class':
        return None
    bid = Class.objects.get(pk=bid_id)
    return get_scheduling_info(bid)


def get_scheduling_info(bid_class):
    if bid_class.__class__.__name__ != 'Class':
        return None
    schedule_opt = dict(class_schedule_options)
    scheduling_info = {
        'display_info': [
            (classbid_labels['schedule_constraints'],
             ', '.join(
                [j for i, j in class_schedule_options
                 if i in bid.schedule_constraints])),
            (classbid_labels['avoided_constraints'],
             ', '.join(
                [j for i, j in class_schedule_options
                 if i in bid.avoided_constraints])),
            ('Format', bid.type),
            ('Space Needs', bid.get_space_needs_display()),
            ],
        'reference': reverse('class_view',
                             urlconf='gbe.urls',
                             args=[bid.id]),
        }

    return scheduling_info
