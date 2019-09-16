from gbe.views import BidChangeStateView
from gbe.models import Vendor


class VendorChangeStateView(BidChangeStateView):
    object_type = Vendor
    coordinator_permissions = ('Vendor Coordinator', )
    redirectURL = 'vendor_review_list'

    def get_bidder(self):
        self.bidder = self.object.profile
