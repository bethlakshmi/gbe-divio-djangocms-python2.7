from django.core.urlresolvers import reverse
from gbe.models import Vendor
from review_bid_list_view import ReviewBidListView


class ReviewVendorListView(ReviewBidListView):
    reviewer_permissions = ('Vendor Reviewers',)
    object_type = Vendor
    bid_review_view_name = 'vendor_review'
    bid_review_list_view_name = 'vendor_review_list'

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
