from django.urls import reverse
from gbe.models import Vendor
from gbe.views import ReviewBidListView


class ReviewVendorListView(ReviewBidListView):
    reviewer_permissions = ('Vendor Reviewers',)
    object_type = Vendor
    bid_review_view_name = 'vendor_review'
    bid_review_list_view_name = 'vendor_review_list'
    page_title = 'Review Vendors'
    view_title = 'Vendor Proposals'

    def get_context_dict(self):
        context = super(ReviewVendorListView, self).get_context_dict()
        context['order'] = 1
        return context
