from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import Http404
from django.urls import reverse
from gbetext import calendar_type as calendar_type_options
from gbetext import (
    login_please,
    pending_note,
)
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
from gbe.forms import InvolvedProfileForm
from gbe.models import (
    Bio,
    ConferenceDay,
    UserMessage,
)
from gbe.functions import (
    get_current_conference,
    get_conference_days,
    get_conference_by_slug,
    conference_slugs,
    validate_perms,
)
from scheduler.idd import (
    get_bookings,
    get_eval_info,
    get_occurrences,
    get_schedule,
)
from scheduler.data_transfer import Person
from gbe.scheduling.views.functions import show_general_status
from django.conf import settings
from gbe.scheduling.views.functions import build_icon_links


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
    show_editors = ('Scheduling Mavens', 'Act Coordinator')

    def process_inputs(self, request, args, kwargs):
        context = {}
        self.calendar_type = None
        self.conference = None
        self.this_day = None
        self.can_edit_show = False
        if "calendar_type" in kwargs:
            self.calendar_type = kwargs['calendar_type']
            if self.calendar_type not in list(calendar_type_options.values()):
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
        pending_instructions = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="PENDING_INSTRUCTIONS",
            defaults={
                'summary': "Pending Instructions (in modal, approval needed)",
                'description': pending_note})
        login_please_msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="LOGIN_REQUIRED",
            defaults={
                'summary': "Login or setup account message",
                'description': login_please})
        context = {
            'calendar_type': self.calendar_type,
            'conference': self.conference,
            'conference_slugs': conference_slugs(),
            'this_day': self.this_day,
            'pending_note': pending_instructions[0].description,
            'login_please': login_please_msg[0].description,
        }
        if self.calendar_type == "General" and validate_perms(
                request,
                self.show_editors,
                require=False):
            self.can_edit_show = True

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
        hour_block_size = {}
        for occurrence in occurrences:
            role = None
            for booking in personal_schedule:
                if booking.event == occurrence:
                    role = booking.role
            hour = occurrence.start_time.strftime("%-I:00 %p")
            title = occurrence.title
            if occurrence.parent is not None:
                title = "%s: %s" % (occurrence.parent.title, occurrence.title)
                if occurrence.parent.slug is not None:
                    title = "%s: %s" % (occurrence.parent.slug,
                                        occurrence.title)
            occurrence_detail = {
                'object': occurrence,
                'hour': hour,
                'approval_needed': occurrence.approval_needed,
                'title': title,
                'detail_link': reverse('detail_view',
                                       urlconf='gbe.scheduling.urls',
                                       args=[occurrence.pk]),
                'teachers': [],
            }
            if self.can_edit_show and occurrence.event_style == "Show":
                occurrence_detail['show_dashboard'] = reverse(
                    'show_dashboard',
                    urlconf='gbe.scheduling.urls',
                    args=[occurrence.pk])
            for person in get_bookings([occurrence.pk],
                                       roles=["Teacher", "Moderator"]).people:
                presenter = Bio.objects.get(pk=person.public_id)
                occurrence_detail['teachers'] += [(person.role, presenter)]
            (occurrence_detail['favorite_link'],
             occurrence_detail['volunteer_link'],
             occurrence_detail['evaluate'],
             occurrence_detail['highlight'],
             occurrence_detail['vol_disable_msg']) = build_icon_links(
             occurrence,
             eval_occurrences,
             self.calendar_type,
             (self.conference.status == "completed"),
             personal_schedule)

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
            if request.user.is_authenticated and hasattr(
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
                if not request.user.profile.participation_ready:
                    context['complete_profile_form'] = InvolvedProfileForm(
                        instance=request.user.profile,
                        initial={'first_name': request.user.first_name,
                                 'last_name': request.user.last_name})

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
