from django.forms import (
    CheckboxSelectMultiple,
    HiddenInput,
    ModelForm,
    MultipleChoiceField,
)
from gbe.models import Vendor
from gbe_forms_text import (
    vendor_help_texts,
    vendor_labels,
    vendor_schedule_options,
)
from gbe.expoformfields import FriendlyURLInput
from django_addanother.widgets import AddAnotherEditSelectedWidgetWrapper
from dal import autocomplete
from django.urls import reverse_lazy


class VendorBidForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    help_times = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=vendor_schedule_options,
        required=False,
        label=vendor_labels['help_times'])

    def __init__(self, *args, **kwargs):
        super(VendorBidForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Vendor
        fields = ['business',
                  'want_help',
                  'help_description',
                  'help_times',
                  ]
        help_texts = vendor_help_texts
        labels = vendor_labels
        widgets = {
            'accepted': HiddenInput(),
            'submitted': HiddenInput(),
            'business': AddAnotherEditSelectedWidgetWrapper(
                autocomplete.ModelSelect2(
                    url=reverse_lazy('limited-business-autocomplete',
                                     urlconf='gbe.urls')),
                reverse_lazy('business-add', urlconf='gbe.urls'),
                reverse_lazy('business-update',
                             urlconf='gbe.urls',
                             args=['__fk__'])),
        }
