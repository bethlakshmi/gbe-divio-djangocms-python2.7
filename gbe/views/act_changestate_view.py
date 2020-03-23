from django.contrib import messages
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from gbe_logging import log_func
from scheduler.models import (
    ActResource,
    ResourceAllocation,
)
from django.utils.formats import date_format
from gbe.views import BidChangeStateView
from gbe.models import (
    Act,
    ActCastingOption,
    GenericEvent,
    Show,
    UserMessage,
)
from gbe.email.functions import send_bid_state_change_mail
from gbetext import no_casting_msg
from scheduler.idd import (
    get_occurrences,
    get_schedule,
    remove_booking,
    set_act,
)
from gbe.scheduling.views.functions import show_general_status
from scheduler.data_transfer import BookableAct
from django.http import Http404


class ActChangeStateView(BidChangeStateView):
    object_type = Act
    coordinator_permissions = ('Act Coordinator',)
    redirectURL = 'act_review_list'
    new_show = None
    show_booked_states = (3, 2)

    def get_bidder(self):
        self.bidder = self.object.performer.contact

    def act_accepted(self, request):
        return (request.POST['show'] and
                int(request.POST['accepted']) in self.show_booked_states)

    def parse_act_schedule(self, schedule_items):
        show = None
        rehearsals = []
        for item in schedule_items:
            if Show.objects.filter(
                    eventitem_id=item.event.eventitem.eventitem_id).exists():
                show = item
            elif item.event not in rehearsals and GenericEvent.objects.filter(
                    eventitem_id=item.event.eventitem.eventitem_id,
                    type='Rehearsal Slot').exists():
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
            response = get_schedule(act=self.object)
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
            if request.POST['accepted'] == '2':
                casting = "Waitlisted"
            # because at the time of this comment, not all waitlisted acts
            # have a role of waitlisted.  Can be removed after 2020.
            if self.object.accepted == 2:
                role = "Waitlisted"
            same_show = False
            same_role = False
            if show and show.event.eventitem == self.new_show.eventitem:
                same_show=True
                if casting == show.role:
                    same_role = True

            # if both show and role are same, do nothing
            if same_show and not same_role:
                set_response = set_act(act=BookableAct(
                    act=self.object,
                    booking_id=show.booking_id,
                    role=casting))
                show_general_status(set_response,
                                    response,
                                    self.__class__.__name__)
                if self.object.accepted == 2:
                    self.clear_bookings(request, rehearsals)
            elif not same_show:
                self.clear_bookings(request, rehearsals, show)
                set_response = set_act(
                    occurrence_id=self.new_show.pk,
                    act=BookableAct(act=self.object,
                                    role=casting))
                show_general_status(set_response,
                                    response,
                                    self.__class__.__name__)

            for worker in self.object.get_performer_profiles():
                conflicts = worker.get_conflicts(self.new_show)
                for problem in conflicts:
                    messages.warning(
                        request,
                        "%s is booked for - %s - %s" % (
                            str(worker),
                            str(problem),
                            date_format(
                                problem.starttime,
                                "DATETIME_FORMAT")
                        )
                    )
        else:
            self.clear_bookings(request, rehearsals, show)

        return super(ActChangeStateView, self).bid_state_change(
            request)

    def notify_bidder(self, request):
        email_show = None
        if (str(self.object.accepted) != request.POST['accepted']) or (
                request.POST['accepted'] == '3'):
            # only send the show when act is accepted
            if request.POST['accepted'] == '3':
                email_show = self.new_show
            email_status = send_bid_state_change_mail(
                str(self.object_type.__name__).lower(),
                self.bidder.contact_email,
                self.bidder.get_badge_name(),
                self.object,
                int(request.POST['accepted']),
                show=email_show)
            self.check_email_status(request, email_status)

    def prep_bid(self, request, args, kwargs):
        super(ActChangeStateView, self).prep_bid(request, args, kwargs)
        if self.act_accepted(request):
            response = get_occurrences(
                foreign_event_ids=[request.POST['show']])
            show_general_status(request, response, self.__class__.__name__)
            if response.occurrences.count() > 0:
                self.new_show = response.occurrences.first()
            else:
                raise Http404
 
