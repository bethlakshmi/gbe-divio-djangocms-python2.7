from django.views.generic import View
from django.shortcuts import (
    render,
)
from gbe.scheduling.views.functions import (
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
        if request.user.is_authenticated() and request.user.profile:
            person = Person(
                user=request.user,
                public_id=request.user.profile.pk,
                public_class="Profile")
            personal_schedule_items = get_schedule(
                request.user,
                labels=[
                    eventitem_view['event'].calendar_type,
                    eventitem_view['event'].e_conference.conference_slug]
                ).schedule_items
        for occurrence in eventitem_view['scheduled_events']:
            schedule_item = {
                'occurrence': occurrence,
                'favorite_link': reverse(
                    'set_favorite',
                    args=[occurrence.pk, 'on'],
                    urlconf='gbe.scheduling.urls'),
                'highlight': None,
                'evaluate': None
            }
            if eventitem_view['event'].calendar_type == "Volunteer" or (
                    eventitem_view['event'].e_conference.status == "completed"
                    ):
                schedule_item['favorite_link'] = None
            if eventitem_view['event'].calendar_type == "Conference":
                eval_response = get_eval_info(occurrence_id=occurrence.pk,
                                              person=person)
                if len(eval_response.questions) > 0:
                    if person and len(eval_response.answers) > 0:
                        schedule_item['evaluate'] = "disabled"
                    else:
                        schedule_item['evaluate'] = reverse(
                            'eval_event',
                            args=[occurrence.pk, ],
                            urlconf='gbe.scheduling.urls')

            for booking in personal_schedule_items:
                if booking.event == occurrence:
                    schedule_item['highlight'] = booking.role.lower()
                    if booking.role == "Interested":
                        schedule_item['favorite_link'] = reverse(
                            'set_favorite',
                            args=[occurrence.pk, 'off'],
                            urlconf='gbe.scheduling.urls')
                    else:
                        schedule_item['favorite_link'] = "disabled"
                        schedule_item['evaluate'] = None

            schedule_items += [schedule_item]
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
