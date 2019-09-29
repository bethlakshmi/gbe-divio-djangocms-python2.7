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
from scheduler.idd import (
    get_bookings,
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
)
from datetime import (
    datetime,
    timedelta,
)
import pytz
from django.conf import settings


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

        if event_type in map(lambda x: x.lower(), event_types.keys()):
            items = GenericEvent.objects.filter(
                type__iexact=event_type,
                visible=True,
                e_conference=self.conference).order_by('e_title')
        elif event_type.title() in class_types.keys():
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
        else:
            items = []
        return items

    def get(self, request, *args, **kwargs):
        context = self.setup(request, args, kwargs)
        items = self.get_events_list_by_type()
        events = []
        eval_occurrences = []
        if request.user.is_authenticated() and hasattr(request.user,
                                                       'profile'):
            person = Person(
                user=request.user,
                public_id=request.user.profile.pk,
                public_class="Profile")
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
                evaluate = None
                people_response = get_bookings([occurrence.pk])
                highlight = None
                role = None
                favorite_link = reverse(
                    'set_favorite',
                    args=[occurrence.pk, 'on'],
                    urlconf='gbe.scheduling.urls')
                for person in people_response.people:
                    if request.user == person.user:
                        role = person.role
                        highlight = person.role.lower()
                        if person.role == "Interested":
                            favorite_link = reverse(
                                'set_favorite',
                                args=[occurrence.pk, 'off'],
                                urlconf='gbe.scheduling.urls')
                        else:
                            favorite_link = "disabled"
                    if person.role in (
                            "Teacher",
                            "Moderator",
                            "Panelist") and person.public_class != "Profile":
                        presenter = Performer.objects.get(pk=person.public_id)
                        if presenter not in presenters:
                            presenters += [presenter]
                if self.conference.status == "completed" or (
                        item.calendar_type == 'Volunteer'):
                    favorite_link = None
                if (self.event_type == 'Class') and (
                        occurrence.start_time < (datetime.now() - timedelta(
                            hours=settings.EVALUATION_WINDOW))
                        ) and (
                        role not in ("Teacher", "Performer", "Moderator")
                        ) and (
                        eval_occurrences is not None):
                    if occurrence in eval_occurrences:
                        evaluate = "disabled"
                    else:
                        evaluate = reverse(
                            'eval_event',
                            args=[occurrence.pk, ],
                            urlconf='gbe.scheduling.urls')
                scheduled_events += [{
                    'occurrence': occurrence,
                    'favorite_link': favorite_link,
                    'highlight': highlight,
                    'evaluate': evaluate,
                }]
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
