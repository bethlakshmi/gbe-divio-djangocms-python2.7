from gbe_logging import log_func
from gbe.models import Volunteer
from gbe.views import BidChangeStateView
from scheduler.idd import (
    set_person,
    remove_person,
)
from gbe.email.functions import send_schedule_update_mail
from gbe.scheduling.views.functions import show_general_status
from scheduler.data_transfer import (
    Person,
)


class VolunteerChangeStateView(BidChangeStateView):
    object_type = Volunteer
    coordinator_permissions = ('Volunteer Coordinator',)
    redirectURL = 'volunteer_review_list'

    def get_bidder(self):
        self.bidder = self.object.profile

    def groundwork(self, request, args, kwargs):
        self.prep_bid(request, args, kwargs)
        if request.POST['accepted'] != '3':
            self.notify_bidder(request)

    @log_func
    def bid_state_change(self, request):
        # Clear all commitments
        remove_response = remove_person(
            user=self.bidder.user_object,
            labels=[self.object.b_conference.conference_slug],
            roles=['Volunteer'])
        show_general_status(request, remove_response, self.__class__.__name__)

        # if the volunteer has been accepted, set the events.
        if request.POST['accepted'] == '3':
            person = Person(
                    user=self.bidder.user_object,
                    public_id=self.bidder.pk,
                    role='Volunteer')
            for assigned_event in request.POST.getlist('events'):
                set_response = set_person(
                    assigned_event,
                    person)
                show_general_status(request,
                                    set_response,
                                    self.__class__.__name__)

            email_status = send_schedule_update_mail('Volunteer', self.bidder)
            self.check_email_status(request, email_status)

        return super(VolunteerChangeStateView, self).bid_state_change(
            request)
