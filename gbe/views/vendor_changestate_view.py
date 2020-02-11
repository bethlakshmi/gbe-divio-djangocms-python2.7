from gbe.views import BidChangeStateView
from gbe.models import Vendor
from gbe.forms import VendorStateChangeForm


class VendorChangeStateView(BidChangeStateView):
    object_type = Vendor
    coordinator_permissions = ('Vendor Coordinator', )
    redirectURL = 'vendor_review_list'
    bid_state_change_form = VendorStateChangeForm

    def get_bidder(self):
        self.bidder = self.object.profile
