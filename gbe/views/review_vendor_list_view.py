from django.urls import reverse
from gbe.models import Vendor
from gbe.views import ReviewBidListView


class ReviewVendorListView(ReviewBidListView):
    reviewer_permissions = ('Vendor Reviewers',)
    object_type = Vendor
    bid_review_view_name = 'vendor_review'
    bid_review_list_view_name = 'vendor_review_list'

    def get_context_dict(self):
        return {'columns': self.object_type().bid_review_header,
                'rows': self.rows,
                'order': 1,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
