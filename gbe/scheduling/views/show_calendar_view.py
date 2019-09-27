from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import Http404
from django.core.urlresolvers import reverse
from gbetext import calendar_type as calendar_type_options
from django.utils.formats import date_format
from settings import (
    TIME_FORMAT,
    URL_DATE,
)
from datetime import (
    datetime,
    timedelta,
)
import pytz
from gbe.models import (
    ConferenceDay,
    Event,
)
from gbe.functions import (
    get_current_conference,
    get_conference_days,
    get_conference_by_slug,
    conference_slugs,
)
from scheduler.idd import (
    get_eval_info,
    get_occurrences,
    get_schedule,
)
from scheduler.data_transfer import Person
from gbe.scheduling.views.functions import show_general_status
from django.conf import settings


class ShowCalendarView(View):
    template = 'gbe/scheduling/calendar.tmpl'
    calendar_type = None
    conference = None
    this_day = None
    grid_map = {
        5: 3,
        4: 3,
        3: 4,
        2: 6,
        1: 12,
    }

    def process_inputs(self, request, args, kwargs):
        context = {}
        self.calendar_type = None
        self.conference = None
        self.this_day = None
        if "calendar_type" in kwargs:
            self.calendar_type = kwargs['calendar_type']
            if self.calendar_type not in calendar_type_options.values():
                raise Http404

        if "day" in self.request.GET:
            try:
                self.this_day = get_object_or_404(
                    ConferenceDay,
                    day=datetime.strptime(self.request.GET.get('day', None),
                                          URL_DATE))
            except ValueError:
                raise Http404
            self.conference = self.this_day.conference

        elif "conference" in self.request.GET:
            self.conference = get_conference_by_slug(
                self.request.GET.get('conference', None))
        else:
            self.conference = get_current_conference()

        if not self.this_day:
            self.this_day = get_conference_days(
                self.conference,
                open_to_public=True).order_by("day").first()

        context = {
            'calendar_type': self.calendar_type,
            'conference': self.conference,
            'conference_slugs': conference_slugs(),
            'this_day': self.this_day,
        }
        if self.this_day:
            open_to_public = [True]
            if self.calendar_type == "Volunteer":
                open_to_public = [True, False]
            if ConferenceDay.objects.filter(
                    day=self.this_day.day+timedelta(days=1),
                    open_to_public__in=open_to_public).exists():
                context['next_date'] = (self.this_day.day+timedelta(days=1)
                                        ).strftime(URL_DATE)
            if ConferenceDay.objects.filter(
                    day=self.this_day.day-timedelta(days=1),
                    open_to_public__in=open_to_public).exists():
                context['prev_date'] = (self.this_day.day-timedelta(days=1)
                                        ).strftime(URL_DATE)

        return context

    def build_occurrence_display(self,
                                 occurrences,
                                 personal_schedule=None,
                                 eval_occurrences=None):
        display_list = []
        events = Event.objects.filter(e_conference=self.conference)
        hour_block_size = {}
        for occurrence in occurrences:
            role = None
            for booking in personal_schedule:
                if booking.event == occurrence:
                    role = booking.role
            event = events.filter(pk=occurrence.eventitem.event.pk).first()
            hour = occurrence.start_time.strftime("%-I:00 %p")
            occurrence_detail = {
                'start':  occurrence.start_time.strftime(TIME_FORMAT),
                'end': occurrence.end_time.strftime(TIME_FORMAT),
                'title': event.e_title,
                'location': occurrence.location,
                'hour': hour,
                'detail_link': reverse('detail_view',
                                       urlconf='gbe.scheduling.urls',
                                       args=[occurrence.eventitem.pk]),
            }
            if self.conference.status != "completed":
                occurrence_detail['favorite_link'] = reverse(
                    'set_favorite',
                    args=[occurrence.pk, 'on'],
                    urlconf='gbe.scheduling.urls')
                if role == "Interested":
                    occurrence_detail['favorite_link'] = reverse(
                        'set_favorite',
                        args=[occurrence.pk, 'off'],
                        urlconf='gbe.scheduling.urls')
                elif role is not None:
                    occurrence_detail['favorite_link'] = "disabled"
                if role:
                    occurrence_detail['highlight'] = role.lower()
            if (self.calendar_type == 'Volunteer') and (
                    'favorite_link' in occurrence_detail) and (
                    occurrence_detail['favorite_link'] != "disabled"):
                occurrence_detail['favorite_link'] = None
            if (self.calendar_type == 'Conference') and (
                    occurrence.start_time < (datetime.now() - timedelta(
                        hours=settings.EVALUATION_WINDOW))
                    ) and (
                    role not in ("Teacher", "Performer", "Moderator")) and (
                    eval_occurrences is not None):
                if occurrence in eval_occurrences:
                    occurrence_detail['evaluate'] = "disabled"
                else:
                    occurrence_detail['evaluate'] = reverse(
                        'eval_event',
                        args=[occurrence.pk, ],
                        urlconf='gbe.scheduling.urls')
            display_list += [occurrence_detail]
            if hour in hour_block_size:
                hour_block_size[hour] += 1
            else:
                hour_block_size[hour] = 1
        return max(hour_block_size.values()), display_list

    def get(self, request, *args, **kwargs):
        context = self.process_inputs(request, args, kwargs)
        personal_schedule = []
        eval_occurrences = []
        if not self.conference or not self.this_day or not self.calendar_type:
            return render(request, self.template, context)
        response = get_occurrences(
            labels=[self.calendar_type, self.conference.conference_slug],
            day=self.this_day.day)
        show_general_status(
            request, response, self.__class__.__name__)
        if len(response.occurrences) > 0:
            if request.user.is_authenticated() and hasattr(
                    request.user,
                    'profile'):
                sched_response = get_schedule(
                    request.user,
                    labels=[self.calendar_type,
                            self.conference.conference_slug])
                personal_schedule = sched_response.schedule_items
                person = Person(
                    user=request.user,
                    public_id=request.user.profile.pk,
                    public_class="Profile")
                eval_response = get_eval_info(person=person)
                if len(eval_response.questions) > 0:
                    eval_occurrences = eval_response.occurrences
                else:
                    eval_occurrences = None
            max_block_size, context[
                'occurrences'] = self.build_occurrence_display(
                response.occurrences,
                personal_schedule,
                eval_occurrences)
            grid_size = 2
            if max_block_size < 6:
                grid_size = self.grid_map[max_block_size]
            context['grid_size'] = grid_size
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ShowCalendarView, self).dispatch(*args, **kwargs)
