from django.core.urlresolvers import reverse
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
)


def get_scheduling_info(bid_class):
    if bid_class.__class__.__name__ != 'Class':
        return None

    schedule_opt = dict(class_schedule_options)
    scheduling_info = {
        'display_info': [
            (classbid_labels['schedule_constraints'],
             ', '.join(
                [j for i, j in class_schedule_options
                 if i in bid_class.schedule_constraints])),
            (classbid_labels['avoided_constraints'],
             ', '.join(
                [j for i, j in class_schedule_options
                 if i in bid_class.avoided_constraints])),
            ('Format', bid_class.type),
            ('Space Needs', bid_class.get_space_needs_display()),
            ],
        'reference': reverse('class_view',
                             urlconf='gbe.urls',
                             args=[bid_class.id]),
        }

    return scheduling_info
