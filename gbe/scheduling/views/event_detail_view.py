from django.views.generic import View
from django.shortcuts import (
    render,
)
from gbe.scheduling.views.functions import (
    build_icon_links,
    get_event_display_info,
)
from scheduler.idd import (
    get_eval_info,
    get_schedule,
)
from scheduler.data_transfer import Person
from django.core.urlresolvers import reverse


class EventDetailView(View):
    '''
    Takes the id of a single event_item and displays all its
    details in a template
    '''
    def get(self, request, *args, **kwargs):
        eventitem_id = kwargs['eventitem_id']
        schedule_items = []
        personal_schedule_items = []
        eventitem_view = get_event_display_info(eventitem_id)
        person = None
        eval_occurrences = None
        if request.user.is_authenticated() and request.user.profile and (
                eventitem_view['event'].calendar_type):
            person = Person(
                user=request.user,
                public_id=request.user.profile.pk,
                public_class="Profile")
            eval_response = get_eval_info(person=person)
            if len(eval_response.questions) > 0:
                eval_occurrences = eval_response.occurrences

        for occurrence in eventitem_view['scheduled_events']:
            (favorite_link,
             volunteer_link,
             evaluate,
             highlight,
             new_presenters) = build_icon_links(
                occurrence,
                eval_occurrences,
                eventitem_view['event'].calendar_type,
                (eventitem_view['event'].e_conference.status == "completed"),
                request.user)
            schedule_items += [{
                'occurrence': occurrence,
                'favorite_link': favorite_link,
                'volunteer_link': volunteer_link,
                'highlight': highlight,
                'evaluate': evaluate,
                'approval_needed': occurrence.approval_needed,
            }]
        template = 'gbe/scheduling/event_detail.tmpl'
        return render(request,
                      template,
                      {'eventitem': eventitem_view,
                       'show_tickets': True,
                       'tickets': eventitem_view['event'].get_tickets,
                       'user_id': request.user.id,
                       'schedule_items': schedule_items})

    def dispatch(self, *args, **kwargs):
        return super(EventDetailView, self).dispatch(*args, **kwargs)
