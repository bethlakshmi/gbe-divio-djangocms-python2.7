from django.forms import (
    ModelForm,
)
from gbe.models import Biddable
from gbe_forms_text import (
    acceptance_help_texts,
    acceptance_labels,
)


class BidStateChangeForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Biddable
        fields = ['accepted']
        required = ['accepted']
        labels = acceptance_labels
        help_texts = acceptance_help_texts
