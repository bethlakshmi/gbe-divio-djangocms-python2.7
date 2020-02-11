from gbe.models import Vendor
from gbe.forms import BidStateChangeForm
from gbe_forms_text import (
    acceptance_help_texts,
    acceptance_labels,
)


class VendorStateChangeForm(BidStateChangeForm):
    class Meta:
        model = Vendor
        fields = ['accepted', 'level']
        required = ['accepted']
        labels = acceptance_labels
        help_texts = acceptance_help_texts
