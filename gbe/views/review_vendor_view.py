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
    page_title = 'Review Vendor'
    view_title = 'Vendor Proposal'

    def groundwork(self, request, args, kwargs):
        super(ReviewVendorView, self).groundwork(request, args, kwargs)
        self.object_form = self.bid_form_type(instance=self.object,
                                              prefix=self.bid_prefix)
        self.readonlyform_pieces = [self.object_form]

    def make_context(self):
        return {'vendor': self.object,
                'reviewer': self.reviewer,
                'form': self.form,
                'actionform': self.actionform,
                'actionURL': self.actionURL,
                'conference': self.b_conference,
                'old_bid': self.old_bid,
                'page_title': self.page_title,
                'view_title': self.view_title, }
