from django.views.generic import View
from django.shortcuts import (
    render,
)
from gbe.models import (
    Class,
    Conference,
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
from django.urls import reverse
from gbetext import (
    calendar_for_event,
    role_options,
)


class EventDetailView(View):
    '''
    Takes the id of a single event_item and displays all its
    details in a template
    '''
    def get(self, request, *args, **kwargs):
        from ticketing.functions import get_tickets

        occurrence_id = kwargs['eventitem_id']
        schedule_items = []
        personal_schedule_items = []
        eventitem_view = get_event_display_info(occurrence_id)
        person = None
        eval_occurrences = []
        cal_type = calendar_for_event[
            eventitem_view['occurrence'].event_style]
        labels = eventitem_view['occurrence'].labels
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            person = Person(
                user=request.user,
                public_id=request.user.profile.pk,
                public_class="Profile")
            all_roles = []
            for n, m in role_options:
                all_roles += [m]
            personal_schedule_items = get_schedule(
                request.user,
                labels=labels,
                roles=all_roles,
                ).schedule_items
            if cal_type == "Conference":
                eval_response = get_eval_info(person=person)
                if len(eval_response.questions) > 0:
                    eval_occurrences = eval_response.occurrences
                else:
                    eval_occurrences = None
        conference = Conference.objects.filter(
            conference_slug__in=labels)[0]
        (favorite_link,
         volunteer_link,
         evaluate,
         highlight,
         vol_disable_msg) = build_icon_links(
            eventitem_view['occurrence'],
            eval_occurrences,
            cal_type,
            conference,
            personal_schedule_items)

        schedule_items += [{
            'favorite_link': favorite_link,
            'volunteer_link': volunteer_link,
            'highlight': highlight,
            'evaluate': evaluate,
            'approval_needed': eventitem_view['occurrence'].approval_needed,
            'vol_disable_msg': vol_disable_msg,
            }]
        template = 'gbe/scheduling/event_detail.tmpl'
        bid = None
        if (eventitem_view['occurrence'].connected_class is not None) and (
                eventitem_view['occurrence'].connected_class == "Class"):
            bid = Class.objects.get(
                pk=eventitem_view['occurrence'].connected_id)

        return render(request, template, {
            'eventitem': eventitem_view,
            'conference': conference,
            'show_tickets': True,
            'tickets': get_tickets(eventitem_view['occurrence']),
            'user_id': request.user.id,
            'bid': bid,
            'schedule_items': schedule_items})

    def dispatch(self, *args, **kwargs):
        return super(EventDetailView, self).dispatch(*args, **kwargs)
