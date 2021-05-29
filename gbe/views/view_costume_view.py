from gbe.views import ViewBidView

from gbe.forms import (
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
    PersonaForm,
)
from gbe.models import Costume


class ViewCostumeView(ViewBidView):
    bid_type = Costume
    object_form_type = CostumeBidSubmitForm
    object_detail_form_type = CostumeDetailsSubmitForm
    bidder_form_type = PersonaForm
    viewer_permissions = ('Costume Reviewers',)
    bid_prefix = ''
    performer_prefix = "The Performer"

    def get_display_forms(self):
        bid_form = self.object_form_type(instance=self.bid,
                                         prefix=self.bid_prefix)
        detail_form = self.object_detail_form_type(instance=self.bid)
        if self.bid.performer:
            self.performer = self.bid.performer
        return (bid_form, detail_form)

