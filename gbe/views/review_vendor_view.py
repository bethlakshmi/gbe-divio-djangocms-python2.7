from gbe.models import Vendor
from gbe.forms import (
    VendorBidForm,
    VendorStateChangeForm,
)
from gbe.views import ReviewBidView


class ReviewVendorView(ReviewBidView):
    reviewer_permissions = ('Vendor Reviewers',)
    coordinator_permissions = ('Vendor Coordinator',)
    bid_prefix = 'The Vendor'
    bid_form_type = VendorBidForm
    object_type = Vendor
    review_list_view_name = 'vendor_review_list'
    bid_view_name = 'vendor_view'
    changestate_view_name = 'vendor_changestate'
    bid_state_change_form = VendorStateChangeForm

    def groundwork(self, request, args, kwargs):
        super(ReviewVendorView, self).groundwork(request, args, kwargs)
        self.object_form = self.bid_form_type(instance=self.object,
                                              prefix=self.bid_prefix)
        self.readonlyform_pieces = [self.object_form]

    def make_context(self):
        context = super(ReviewVendorView, self).make_context()
        context['vendor'] = self.object
        return context
