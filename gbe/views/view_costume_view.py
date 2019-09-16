from gbe.views import ViewBidView

from gbe.forms import (
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
)
from gbe.models import Costume


class ViewCostumeView(ViewBidView):
    bid_type = Costume
    object_form_type = CostumeBidSubmitForm
    object_detail_form_type = CostumeDetailsSubmitForm
    viewer_permissions = ('Costume Reviewers',)
    bid_prefix = ''

    def get_display_forms(self):
        bid_form = self.object_form_type(instance=self.bid,
                                         prefix=self.bid_prefix)
        detail_form = self.object_detail_form_type(instance=self.bid)
        return (bid_form, detail_form)
