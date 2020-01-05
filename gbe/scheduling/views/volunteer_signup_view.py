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
    GBE_TIME_FORMAT,
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
from collections import OrderedDict


class VolunteerSignupView(View):
    template = 'gbe/scheduling/calendar_with_shadow.tmpl'
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
        self.calendar_type = "Volunteer"
        self.conference = None
        self.this_day = None

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

        # volunteer events happen on non-public days, as well, but we'll
        # default to a public day to start navigation as those tend to have
        # more need for help.
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
            if ConferenceDay.objects.filter(
                    day=self.this_day.day+timedelta(days=1)).exists():
                context['next_date'] = (self.this_day.day+timedelta(days=1)
                                        ).strftime(URL_DATE)
            if ConferenceDay.objects.filter(
                    day=self.this_day.day-timedelta(days=1)).exists():
                context['prev_date'] = (self.this_day.day-timedelta(days=1)
                                        ).strftime(URL_DATE)

        return context

    def build_occurrence_display(self,
                                 occurrences,
                                 personal_schedule=None,
                                 eval_occurrences=None):
        display_list = []
        hour_display_list = OrderedDict()
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
                'start':  occurrence.start_time.strftime(GBE_TIME_FORMAT),
                'end': occurrence.end_time.strftime(GBE_TIME_FORMAT),
                'title': event.e_title,
                'location': occurrence.location,
                'description': event.e_description,
                'eventitem': occurrence.eventitem,
            }
            if self.conference.status != "completed" and (
                    self.calendar_type == "Volunteer"):
                occurrence_detail['volunteer_link'] = reverse(
                    'set_volunteer',
                    args=[occurrence.pk, 'on'],
                    urlconf='gbe.scheduling.urls')
                if role == "Volunteer" or role == "Pending Volunteer":
                    occurrence_detail['volunteer_link'] = reverse(
                        'set_volunteer',
                        args=[occurrence.pk, 'off'],
                        urlconf='gbe.scheduling.urls')
                elif role is not None:
                    occurrence_detail['volunteer_link'] = "disabled"
                elif occurrence.extra_volunteers() >= 0:
                    occurrence_detail['volunteer_link'] = "full"
                if role:
                    occurrence_detail['highlight'] = role.lower()
            display_list += [occurrence_detail]
            if (hour in hour_display_list):
                hour_display_list[hour][
                    'starting_events'] += [occurrence_detail]
            else:
                hour_display_list[hour] = {
                    'starting_events': [occurrence_detail],
                    'continuing_events': [],
                }
            start_time_copy = occurrence.start_time
            each_hour = start_time_copy.replace(
                minute=0,
                second=0,
                microsecond=0) + timedelta(hours=1)
            print occurrence
            while each_hour < occurrence.end_time:
                print each_hour
                hour_key = each_hour.strftime("%-I:00 %p")
                if (hour_key in hour_display_list):
                    hour_display_list[hour_key][
                        'continuing_events'] += [occurrence_detail]
                else:
                    hour_display_list[hour_key] = {
                        'starting_events': [],
                        'continuing_events': [occurrence_detail],
                    }
                each_hour = each_hour + timedelta(hours=1)
            if hour in hour_block_size:
                hour_block_size[hour] += 1
            else:
                hour_block_size[hour] = 1

        return max(hour_block_size.values()), display_list, hour_display_list

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
                'occurrences'], context[
                'occurrences_by_hour'] = self.build_occurrence_display(
                response.occurrences,
                personal_schedule,
                eval_occurrences)
            grid_size = 2
            if max_block_size < 6:
                grid_size = self.grid_map[max_block_size]
            context['grid_size'] = grid_size
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(VolunteerSignupView, self).dispatch(*args, **kwargs)
