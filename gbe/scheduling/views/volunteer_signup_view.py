from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from gbetext import (
    pending_note,
    role_options,
    volunteer_instructions,
)
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
    UserMessage,
)
from gbe.forms import InvolvedProfileForm
from gbe.functions import (
    check_user_and_redirect,
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
from django.http import HttpResponseRedirect


class VolunteerSignupView(View):
    template = 'gbe/scheduling/volunteer_signup.tmpl'
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
                 time(int(mins/60), mins % 60).strftime("%-I%p"),
                 time(int(mins/60), mins % 60),
                 wrap
                 ) for mins in range(
                 start_min,
                 end_min,
                 step)]

    def process_inputs(self, request, args, kwargs):
        context = {}
        self.conference = None
        self.this_day = None

        if "day" in self.request.GET:
            self.this_day = get_object_or_404(
                ConferenceDay,
                day=datetime.strptime(self.request.GET.get('day', None),
                                      URL_DATE))
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
        instructions = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="VOLUNTEER_INSTRUCTIONS",
            defaults={
                'summary': "Volunteer Instructions (in header)",
                'description': volunteer_instructions})
        pending_instructions = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="PENDING_INSTRUCTIONS",
            defaults={
                'summary': "Pending Instructions (in modal, approval needed)",
                'description': pending_note})
        context = {
            'conference': self.conference,
            'this_day': self.this_day,
            'view_header_text': instructions[0].description,
            'pending_note': pending_instructions[0].description,
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
                                 personal_schedule=None):
        display_list = []
        events = Event.objects.filter(e_conference=self.conference)
        for occurrence in occurrences:
            role = None
            for booking in personal_schedule:
                if booking.event == occurrence:
                    if booking.role == "Waitlisted":
                        role = "Pending Volunteer"
                    else:
                        role = booking.role
            roles = ("Volunteer", "Pending Volunteer")
            # if this isn't something they can signup or un-signup for, skip
            if (occurrence.extra_volunteers() < 0 and (
                    role is None or role in roles)) or (
                    role is not None and role in roles):
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
                        slug__in=occurrence.labels)}
                if hasattr(occurrence, 'parent'):
                    occurrence_detail['parent_event'] = occurrence.parent
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
        this_url = reverse(
            'volunteer_signup',
            urlconf='gbe.scheduling.urls')
        response = check_user_and_redirect(
            request,
            this_url,
            self.__class__.__name__)
        if response['error_url']:
            return HttpResponseRedirect(response['error_url'])
        context = self.process_inputs(request, args, kwargs)
        personal_schedule = []
        if not self.conference or not self.this_day:
            return render(request, self.template, context)
        response = get_occurrences(
            labels=["Volunteer", self.conference.conference_slug],
            day=self.this_day.day,
            max_volunteer=1)
        show_general_status(
            request, response, self.__class__.__name__)
        if len(response.occurrences) > 0:
            all_roles = []
            for n, m in role_options:
                all_roles += [m]
            sched_response = get_schedule(
                request.user,
                labels=["Volunteer", self.conference.conference_slug],
                roles=all_roles)
            personal_schedule = sched_response.schedule_items
            person = Person(
                user=request.user,
                public_id=request.user.profile.pk,
                public_class="Profile")
            eval_response = get_eval_info(person=person)
            if not request.user.profile.participation_ready:
                context['complete_profile_form'] = InvolvedProfileForm(
                    instance=request.user.profile,
                    initial={'first_name': request.user.first_name,
                             'last_name': request.user.last_name})
            context['occurrences'] = self.build_occurrence_display(
                response.occurrences,
                personal_schedule)
            context['col_per_hour'] = self.col_per_hour
            context['grid_list'] = self.make_time_range(
                self.start_grid_hour*60,
                self.end_grid_hour*60,
                int(60/self.col_per_hour))
            if self.next_day_end:
                # hack to roll around the clock
                context['grid_list'] += self.make_time_range(
                    self.end_grid_hour*60,
                    (self.end_grid_hour+1)*60,
                    int(60/self.col_per_hour))
                context['grid_list'] += self.make_time_range(
                    0,
                    self.next_day_end*60,
                    int(60/self.col_per_hour),
                    True)
            context['col_fraction'] = 100.0/len(context['grid_list'])

        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(VolunteerSignupView, self).dispatch(*args, **kwargs)
