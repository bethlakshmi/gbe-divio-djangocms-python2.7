from gbe.models import Vendor
from gbe.forms import VendorBidForm
from gbe.views import ViewBidView


class ViewVendorView(ViewBidView):
    bid_type = Vendor
    viewer_permissions = ('Vendor Reviewers',)
    object_form_type = VendorBidForm
    bid_prefix = "The Business"
    owner_prefix = "The Contact Info"

    def make_context(self):
        context = self.get_messages()
        context['vendor'] = self.bid
        return context
