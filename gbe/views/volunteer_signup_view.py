from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import (
    render,
)
from gbe.models import (
    Conference,
    GenericEvent,
    StaffArea,
    UserMessage,
)
from gbe_logging import log_func
from gbe.functions import validate_profile
from gbetext import (
    invalid_volunteer_event,
    no_profile_msg,
    no_login_msg,
    full_login_msg,
    volunteer_signup_instructions,
)
from gbe.scheduling.views.functions import show_general_status
from scheduler.idd import (
    get_occurrence,
    get_occurrences,
    get_schedule,
    remove_person,
    set_person,
)
from scheduler.data_transfer import Person
from gbe.email.functions import send_schedule_update_mail


class VolunteerSignupView(View):
    form = None
    popup_text = None

    def groundwork(self, request, args, kwargs):
        self.profile = validate_profile(request, require=False)
        if not self.profile or not self.profile.complete:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PROFILE_INCOMPLETE",
                defaults={
                    'summary': "Profile Incomplete",
                    'description': no_profile_msg})
            messages.warning(request, user_message[0].description)
            return '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'),
                reverse('volunteer_signup', urlconf='gbe.urls'))

        self.conference = Conference.objects.filter(
                    accepting_bids=True).first()

    def get_bookings(self, request):
        sched_response = get_schedule(
            user=self.profile.user_object,
            labels=[self.conference.conference_slug, ],
            roles=['Volunteer', ])
        show_general_status(request, sched_response, "VolunteerSignup")
        booking_ids = []
        for schedule_item in sched_response.schedule_items:
            booking_ids += [schedule_item.event.pk]
        return request, booking_ids

    def make_context(self, request):
        volunteer_opps = []
        response = get_occurrences(
            labels=[self.conference.conference_slug],
            max_volunteer=1)
        show_general_status(request, response, "VolunteerSignup")
        rehearsals = GenericEvent.objects.filter(
            type='Rehearsal Slot', e_conference=self.conference
            ).values_list('eventitem_id', flat=True)
        request, booking_ids = self.get_bookings(request)

        for event in response.occurrences:
            if (event.extra_volunteers() < 0 or event.pk in booking_ids) and (
                    event.foreign_event_id not in rehearsals):
                volunteer_opp = {
                    'occurrence': event,
                    'booked': event.pk in booking_ids,
                    'eventitem': event.eventitem,
                    'staff_areas': StaffArea.objects.filter(
                        conference=self.conference,
                        slug__in=event.labels.values_list('text', flat=True))
                }
                if hasattr(event, 'container_event'):
                    volunteer_opp['parent_event'] = event.container_event.parent_event
                volunteer_opps += [volunteer_opp]
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="INSTRUCTIONS",
            defaults={
                'summary': "Volunteer Signup Instructions",
                'description': volunteer_signup_instructions})
        return request, {'conference': self.conference,
                         'volunteer_opps': volunteer_opps,
                         'instructions': user_message[0].description}

    @never_cache
    @log_func
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            follow_on = '?next=%s' % reverse(
                'volunteer_signup', urlconf='gbe.urls')
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="USER_NOT_LOGGED_IN",
                defaults={
                    'summary': "Need Login - %s Bid",
                    'description': no_login_msg})
            full_msg = full_login_msg % (
                user_message[0].description,
                reverse('login', urlconf='gbe.urls') + follow_on)
            messages.warning(request, full_msg)

            return HttpResponseRedirect(
                reverse('register', urlconf='gbe.urls') + follow_on)

        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return HttpResponseRedirect(redirect)

        request, context = self.make_context(request)
        return render(
            request,
            'gbe/volunteer_signup.tmpl',
            context)

    @never_cache
    @log_func
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return HttpResponseRedirect(redirect)
        selected_events = []
        for event in request.POST.getlist('events'):
            selected_events += [int(event)]
        request, booking_ids = self.get_bookings(request)
        remove_ids = []
        rehearsals = GenericEvent.objects.filter(
            type='Rehearsal Slot', e_conference=self.conference
            ).values_list('eventitem_id', flat=True)
        for booking_id in booking_ids:
            if booking_id not in selected_events:
                remove_ids += [booking_id]
        if len(remove_ids) > 0:
            remove_response = remove_person(
                user=self.profile.user_object,
                labels=[self.conference.conference_slug],
                roles=['Volunteer', 'Pending Volunteer'],
                occurrence_ids=remove_ids)
            show_general_status(request,
                                remove_response,
                                self.__class__.__name__)
        for assigned_event in selected_events:
            if assigned_event not in booking_ids:
                response = get_occurrence(assigned_event)
                show_general_status(request, response, "VolunteerSignup")
                if response.occurrence and (
                        response.occurrence.extra_volunteers() < 0) and (
                        response.occurrence.foreign_event_id not in rehearsals):
                    allowed_role = "Volunteer"
                    if response.occurrence.approval_needed:
                        allowed_role = "Pending Volunteer"
                    set_response = set_person(
                        assigned_event,
                        Person(
                            user=self.profile.user_object,
                            public_id=self.profile.pk,
                            role=allowed_role))
                    show_general_status(request,
                                        set_response,
                                        self.__class__.__name__)
                elif response.occurrence:
                    user_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="INVALID_EVENT",
                        defaults={
                            'summary': "Invalid Event (event name appended)",
                            'description': invalid_volunteer_event})
                    messages.error(
                        request,
                        user_message[0].description + str(
                            response.occurrence.eventitem))

        send_schedule_update_mail('Volunteer', self.profile)
        # not checking status of sending email, as this is a public thread
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    def dispatch(self, *args, **kwargs):
        return super(VolunteerSignupView, self).dispatch(*args, **kwargs)
