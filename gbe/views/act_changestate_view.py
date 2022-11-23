from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from gbe_logging import log_func
from django.utils.formats import date_format
from gbe.views import BidChangeStateView
from gbe.models import (
    Act,
    ActCastingOption,
    UserMessage,
)
from gbe.email.functions import send_bid_state_change_mail
from gbetext import (
    acceptance_states,
    act_status_change_msg,
    act_status_no_change_msg,
    no_casting_msg,
)
from scheduler.idd import (
    get_occurrence,
    get_schedule,
    remove_booking,
    set_person,
)
from gbe.scheduling.views.functions import show_general_status
from scheduler.data_transfer import (
    Commitment,
    Person,
)
from django.http import Http404


class ActChangeStateView(BidChangeStateView):
    object_type = Act
    coordinator_permissions = ('Act Coordinator',
                               'Technical Director',
                               'Producer',
                               'Stage Manager')
    redirectURL = 'act_review_list'
    new_show = None
    show_booked_states = (3, 2)

    def act_accepted(self, request):
        return ('show' in request.POST) and (
                int(request.POST['accepted']) in self.show_booked_states)

    def parse_act_schedule(self, schedule_items):
        show = None
        rehearsals = []
        for item in schedule_items:
            if item.event.event_style == "Show":
                show = item
            elif item.event not in rehearsals and (
                    item.event.event_style == 'Rehearsal Slot'):
                rehearsals += [item]
        return show, rehearsals

    def clear_bookings(self, request, rehearsals, show=None):
        for item in rehearsals:
            response = remove_booking(item.event.pk,
                                      item.booking_id)
            show_general_status(request, response, self.__class__.__name__)
        if show:
            response = remove_booking(show.event.pk,
                                      show.booking_id)
            show_general_status(request, response, self.__class__.__name__)

    @log_func
    def bid_state_change(self, request):
        show = None
        rehearsals = []

        # Determine if the current show should be changed
        if self.object.accepted in self.show_booked_states:
            response = get_schedule(commitment=self.object,
                                    roles=["Performer", "Waitlisted"])
            show_general_status(request, response, self.__class__.__name__)
            show, rehearsals = self.parse_act_schedule(response.schedule_items)

        # if the act has been accepted, set the show.
        if self.act_accepted(request):
            # Cast the act into the show by adding it to the schedule
            # resource time
            if ('casting' not in request.POST) or (
                    request.POST[
                        'casting'] != '' and ActCastingOption.objects.filter(
                        casting=request.POST['casting']).count() == 0):
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="INVALID_CASTING",
                    defaults={
                        'summary': "Casting Role Incorrect",
                        'description': no_casting_msg})
                messages.error(request, user_message[0].description)

                return HttpResponseRedirect(reverse(
                    "act_review", urlconf='gbe.urls', args=[self.object.pk]))
            casting = request.POST['casting']
            role = "Performer"
            if request.POST['accepted'] == '2':
                casting = "Waitlisted"
                role = "Waitlisted"

            same_show = False
            same_role = False
            if show and show.event == self.new_show:
                same_show = True
                if casting == show.commitment.role:
                    user_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="ACT_NO_CHANGE",
                        defaults={
                            'summary': "Act State Not Changed",
                            'description': act_status_no_change_msg})
                    messages.success(
                        request,
                        "%s<br>Performer/Act: %s - %s" % (
                            user_message[0].description,
                            self.object.performer.name,
                            self.object.b_title))
                    return super(ActChangeStateView, self).bid_state_change(
                        request)

            person = Person(public_id=self.object.performer.pk,
                            role=role,
                            commitment=Commitment(role=casting,
                                                  decorator_class=self.object))
            profiles = self.object.get_performer_profiles()
            if len(profiles) > 1:
                person.users = [profile.user_object for profile in profiles]
            else:
                person.user = profiles[0].user_object
            if same_show and not same_role:
                person.booking_id = show.booking_id
                set_response = set_person(person=person)
                self.show_set_act_status(request, set_response)
                if request.POST['accepted'] != '3':
                    self.clear_bookings(request, rehearsals)
            elif not same_show:
                self.clear_bookings(request, rehearsals, show)
                set_response = set_person(
                    occurrence_id=self.new_show.pk,
                    person=person)
                self.show_set_act_status(request, set_response)

            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ACT_ACCEPTED",
                defaults={
                    'summary': "Act State Changed (Accept/Waitlist)",
                    'description': act_status_change_msg})
            messages.success(
                request,
                "%s<br>Performer/Act: %s - %s<br>State: %s<br>Show: %s" % (
                    user_message[0].description,
                    self.object.performer.name,
                    self.object.b_title,
                    acceptance_states[int(request.POST['accepted'])][1],
                    self.new_show.title))
        else:
            self.clear_bookings(request, rehearsals, show)
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ACT_NOT_ACCEPTED",
                defaults={
                    'summary': "Act State Changed (Not Accepted)",
                    'description': act_status_change_msg})
            messages.success(
                request,
                "%s<br>Performer/Act: %s - %s<br>State: %s" % (
                    user_message[0].description,
                    self.object.performer.name,
                    self.object.b_title,
                    acceptance_states[int(request.POST['accepted'])][1]))

        return super(ActChangeStateView, self).bid_state_change(
            request)

    def show_set_act_status(self, request, set_response):
        more_than_overbooked = False
        for warning in set_response.warnings:
            if warning.code != "OCCURRENCE_OVERBOOKED":
                more_than_overbooked = True
        if more_than_overbooked or len(set_response.errors) > 0:
            show_general_status(request,
                                set_response,
                                self.__class__.__name__)

    def notify_bidder(self, request):
        email_show = None
        if (str(self.object.accepted) != request.POST['accepted']) or (
                request.POST['accepted'] == '3'):
            # only send the show when act is accepted
            if request.POST['accepted'] == '3':
                email_show = self.new_show
            for bidder in self.object.profiles:
                email_status = send_bid_state_change_mail(
                    str(self.object_type.__name__).lower(),
                    bidder.contact_email,
                    bidder.get_badge_name(),
                    self.object,
                    int(request.POST['accepted']),
                    show=email_show)
                self.check_email_status(request, email_status)

    def prep_bid(self, request, args, kwargs):
        super(ActChangeStateView, self).prep_bid(request, args, kwargs)
        if 'next' in request.POST:
            self.next_page = request.POST['next']
        elif 'next' in request.GET:
            self.next_page = request.GET['next']
        if self.act_accepted(request):
            response = get_occurrence(request.POST['show'])
            show_general_status(request, response, self.__class__.__name__)
            if response.occurrence is not None:
                self.new_show = response.occurrence
            else:
                raise Http404
