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
    bid_edit_view_name = 'volunteer_edit'
    bid_assign_view_name = 'volunteer_assign'
    bid_order_fields = ('accepted',)
    status_index = 8

    def _show_edit(self, volunteer):
        return (validate_perms(self.request,
                               self.coordinator_permissions,
                               require=False) and
                volunteer.is_current)

    def row_hook(self, bid, bid_row):
        if self._show_edit(bid):
            bid_row['edit_url'] = reverse(self.bid_edit_view_name,
                                          urlconf='gbe.urls',
                                          args=[bid.id])
            bid_row['assign_url'] = reverse(self.bid_assign_view_name,
                                            urlconf='gbe.urls',
                                            args=[bid.id])

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
