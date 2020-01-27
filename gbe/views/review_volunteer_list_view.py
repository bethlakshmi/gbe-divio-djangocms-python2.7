from django.core.urlresolvers import reverse
from gbe.models import Volunteer
from gbe.functions import validate_perms
from review_bid_list_view import ReviewBidListView


class ReviewVolunteerListView(ReviewBidListView):
    reviewer_permissions = ('Volunteer Reviewers', )
    coordinator_permissions = ('Volunteer Coordinator', )
    object_type = Volunteer
    bid_review_view_name = 'volunteer_review'
    bid_review_list_view_name = 'volunteer_review_list'
    bid_order_fields = ('accepted',)
    status_index = 8

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
