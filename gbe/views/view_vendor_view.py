from gbe.models import Vendor
from gbe.forms import VendorBidForm
from gbe.views import ViewBidView


class ViewVendorView(ViewBidView):
    bid_type = Vendor
    viewer_permissions = ('Vendor Reviewers',)
    object_form_type = VendorBidForm
    bid_prefix = "The Business"
    owner_prefix = "The Contact Info"
    edit_name = "vendor_edit"

    def make_context(self):
        context = {'vendor': self.bid, }
        return context
