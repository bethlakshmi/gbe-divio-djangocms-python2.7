from gbe.models import Volunteer
from gbe.views.volunteer_display_functions import get_volunteer_forms
from gbe.views import ViewBidView


class ViewVolunteerView(ViewBidView):
    bid_type = Volunteer
    viewer_permissions = ('Volunteer Reviewers',)

    def get_display_forms(self):
        return get_volunteer_forms(self.bid)
