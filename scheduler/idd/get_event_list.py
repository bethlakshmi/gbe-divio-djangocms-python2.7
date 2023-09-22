from django.db.models import Q
from scheduler.models import Event
from settings import GBE_DATETIME_FORMAT


def get_event_list(event_style="Volunteer",
                   label=None,
                   text=None):
    qs = Event.objects.filter(event_style=event_style)
    if label:
        qs = qs.filter(eventlabel__text=label)

    if text:
        qs = qs.filter(Q(title__icontains=text) |
                       Q(parent__title__icontains=text))

    event_list = []
    for event in qs.order_by('starttime', 'title'):
        label = "%s - %s" % (event.title,
                             event.starttime.strftime(GBE_DATETIME_FORMAT))
        if event.parent is not None:
            label = event.parent.title + ' - ' + label
        event_list += [(event.pk, label)]
    return event_list
