from django.views.generic import View
from django.shortcuts import (
    render,
)
from django.http import Http404
from django.core.urlresolvers import reverse
from gbe.models import (
    Class,
    Event,
    GenericEvent,
    Performer,
    Show,
)
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    conference_slugs,
)
from gbe.scheduling.views.functions import build_icon_links
from scheduler.idd import (
    get_bookings,
    get_schedule,
    get_eval_info,
    get_occurrences,
)
from scheduler.data_transfer import Person
from gbe_forms_text import (
    list_text,
    list_titles,
)
from gbetext import (
    event_options,
    class_options,
    role_options,
)


class ListEventsView(View):
    template = 'gbe/scheduling/event_display_list.tmpl'
    conference = None
    event_type = "All"

    def setup(self, request, args, kwargs):
        context = {}

        if "event_type" in kwargs:
            self.event_type = kwargs['event_type']
            if self.event_type.lower() not in list_titles:
                raise Http404

        if "conference" in self.request.GET:
            self.conference = get_conference_by_slug(
                self.request.GET.get('conference', None))
        else:
            self.conference = get_current_conference()
        if not self.conference:
            raise Http404

        context = {
            'conf_slug': self.conference.conference_slug,
            'conference_slugs': conference_slugs(),
            'title': list_titles.get(self.event_type.lower(), ""),
            'view_header_text': list_text.get(self.event_type.lower(), ""),
        }

        return context

    def get_events_list_by_type(self):
        event_type = self.event_type.lower()
        items = []
        if event_type == "all":
            return Event.get_all_events(self.conference)

        event_types = dict(event_options)
        class_types = dict(class_options)

        if event_type in [x.lower() for x in list(event_types.keys())]:
            items = GenericEvent.objects.filter(
                type__iexact=event_type,
                visible=True,
                e_conference=self.conference).order_by('e_title')
        elif event_type.title() in list(class_types.keys()):
            items = Class.objects.filter(
                accepted='3',
                visible=True,
                type__iexact=event_type,
                e_conference=self.conference).order_by('e_title')
        elif event_type == 'show':
            items = Show.objects.filter(
                e_conference=self.conference).order_by('e_title')
        elif event_type == 'class':
            items = Class.objects.filter(
                accepted='3',
                visible=True,
                e_conference=self.conference).exclude(
                    type='Panel').order_by('e_title')
        return items

    def get(self, request, *args, **kwargs):
        context = self.setup(request, args, kwargs)
        items = self.get_events_list_by_type()
        events = []
        eval_occurrences = []
        all_roles = []
        personal_schedule_items = []
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            person = Person(
                user=request.user,
                public_id=request.user.profile.pk,
                public_class="Profile")
            for n, m in role_options:
                all_roles += [m]
            personal_schedule_items = get_schedule(
                request.user,
                labels=[self.conference.conference_slug],
                roles=all_roles,
                ).schedule_items

            eval_response = get_eval_info(person=person)
            if len(eval_response.questions) > 0:
                eval_occurrences = eval_response.occurrences
            else:
                eval_occurrences = None
        for item in items:
            scheduled_events = []
            presenters = []
            response = get_occurrences(
                foreign_event_ids=[item.eventitem_id])
            for occurrence in response.occurrences:
                (favorite_link,
                 volunteer_link,
                 evaluate,
                 highlight,
                 vol_disable_msg) = build_icon_links(
                    occurrence,
                    eval_occurrences,
                    item.calendar_type,
                    (self.conference.status == "completed"),
                    personal_schedule_items)
                scheduled_events += [{
                    'occurrence': occurrence,
                    'favorite_link': favorite_link,
                    'volunteer_link': volunteer_link,
                    'highlight': highlight,
                    'evaluate': evaluate,
                    'vol_disable_msg': vol_disable_msg,
                    'approval_needed': occurrence.approval_needed,
                }]
                people_response = get_bookings([occurrence.pk], roles=[
                    "Teacher",
                    "Moderator",
                    "Panelist"])
                for person in people_response.people:
                    if person.public_class != "Profile":
                        presenter = Performer.objects.get(pk=person.public_id)
                        if presenter not in presenters:
                            presenters += [presenter]
            if len(presenters) == 0 and item.calendar_type == "Conference":
                presenters += [item.teacher]

            events += [{
                'eventitem': item,
                'scheduled_events': scheduled_events,
                'presenters': presenters,
                'detail': reverse('detail_view',
                                  urlconf='gbe.scheduling.urls',
                                  args=[item.eventitem_id])}]
        context['events'] = events
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ListEventsView, self).dispatch(*args, **kwargs)
