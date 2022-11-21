from django.forms import (
    BooleanField,
    IntegerField,
    HiddenInput,
    ModelForm,
    TextInput,
)
from gbe_forms_text import (
    classbid_help_texts,
    classbid_labels,
)
from gbe.models import Class


class ClassBookingForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    accepted = IntegerField(
        initial=3,
        widget=HiddenInput)
    submitted = BooleanField(widget=HiddenInput, initial=True)

    class Meta:
        model = Class
        fields = ['type',
                  'b_title',
                  'b_description',
                  'maximum_enrollment',
                  'fee',
                  'accepted',
                  'submitted',
                  'id',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
