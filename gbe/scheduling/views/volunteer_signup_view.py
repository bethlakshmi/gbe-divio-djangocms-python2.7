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
    time,
    timedelta,
)
import pytz
from gbe.models import (
    ConferenceDay,
    Event,
    StaffArea,
)
from gbe.functions import (
    get_current_conference,
    get_conference_days,
    get_conference_by_slug,
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
    template = 'gbe/scheduling/volunteer_signup.tmpl'
    calendar_type = None
    conference = None
    this_day = None
    # 0 = midnight starting day, 23 = 11 pm next day (max)
    start_grid_hour = 7
    end_grid_hour = 23
    # hack to make it possible to roll to midnight and beyond,
    next_day_end = 2
    # number of columns per hour - must be factor of 60, as 60/this = # min
    col_per_hour = 4

    def make_time_range(self, start_min, end_min, step, wrap=False):
        return [(mins % 60 == 0,
                 time(mins/60, mins % 60).strftime("%-I%p"),
                 time(mins/60, mins % 60),
                 wrap
                 ) for mins in range(
                 start_min,
                 end_min,
                 step)]

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
        events = Event.objects.filter(e_conference=self.conference)
        for occurrence in occurrences:
            role = None
            for booking in personal_schedule:
                if booking.event == occurrence:
                    role = booking.role
            # if this isn't something they can signup or un-signup for, skip
            if occurrence.extra_volunteers() < 0 or (
                    role is not None and role not in (
                        "Volunteer", 
                        "Pending Volunteer")):
                event = events.filter(pk=occurrence.eventitem.event.pk).first()
                occurrence_detail = {
                    'object': occurrence,
                    'start':  occurrence.start_time.strftime(GBE_TIME_FORMAT),
                    'end': occurrence.end_time.strftime(GBE_TIME_FORMAT),
                    'colspan': (
                        occurrence.duration.total_seconds() * self.col_per_hour
                        )/3600,
                    'title': event.e_title,
                    'location': occurrence.location,
                    'description': event.e_description,
                    'approval_needed': occurrence.approval_needed,
                    'eventitem': occurrence.eventitem,
                    'staff_areas': StaffArea.objects.filter(
                        conference=self.conference,
                        slug__in=occurrence.labels.values_list('text',
                                                               flat=True))
                }
                if hasattr(occurrence, 'container_event'):
                        occurrence_detail['parent_event'] = \
                            occurrence.container_event.parent_event
                toggle_state = "on"
                if role:
                    toggle_state = "off"
                    occurrence_detail['highlight'] = role.lower()
                occurrence_detail['volunteer_link'] = reverse(
                    'set_volunteer',
                    args=[occurrence.pk, toggle_state],
                    urlconf='gbe.scheduling.urls')
                    
                display_list += [occurrence_detail]

        return display_list

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
            context['occurrences'] = self.build_occurrence_display(
                response.occurrences,
                personal_schedule,
                eval_occurrences)
            #context['start_grid_hour'] = datetime.time(hour=self.start_grid_hour)
            #context['end_grid_hour'] = datetime.time(hour=self.end_grid_hour)
            context['col_per_hour'] = self.col_per_hour
            context['grid_list'] = self.make_time_range(
                self.start_grid_hour*60,
                self.end_grid_hour*60,
                60/self.col_per_hour)
            if self.next_day_end:
                # hack to roll around the clock
                context['grid_list'] += self.make_time_range(
                    self.end_grid_hour*60,
                    (self.end_grid_hour+1)*60,
                    60/self.col_per_hour)
                context['grid_list'] += self.make_time_range(
                    0,
                    self.next_day_end*60,
                    60/self.col_per_hour,
                    True)
            context['col_fraction'] = 100.0/len(context['grid_list'])

        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(VolunteerSignupView, self).dispatch(*args, **kwargs)
