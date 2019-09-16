from django.contrib.auth.decorators import login_required
from gbe.models import Volunteer
from gbe.forms import BidStateChangeForm
from gbe.views import ReviewBidView
from gbe.views.volunteer_display_functions import get_volunteer_forms


class ReviewVolunteerView(ReviewBidView):
    reviewer_permissions = ('Volunteer Reviewers',)
    coordinator_permissions = ('Volunteer Coordinator',)
    object_type = Volunteer
    review_list_view_name = 'volunteer_review_list'
    bid_view_name = 'volunteer_view'
    changestate_view_name = 'volunteer_changestate'

    def get_object(self, request, object_id):
        if int(object_id) == 0:
            object_id = int(request.POST['volunteer'])
        super(ReviewVolunteerView, self).get_object(request, object_id)

    def groundwork(self, request, args, kwargs):
        super(ReviewVolunteerView, self).groundwork(request, args, kwargs)

        self.readonlyform_pieces = get_volunteer_forms(self.object)
