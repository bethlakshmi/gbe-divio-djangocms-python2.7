from django.forms import (
    HiddenInput,
    ModelForm,
)
from gbe.models import Volunteer
from gbe_forms_text import (
    volunteer_help_texts,
    volunteer_labels,
)


class VolunteerBidForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    b_title = HiddenInput()
    description = HiddenInput()

    class Meta:
        model = Volunteer
        fields = ['number_shifts',
                  'opt_outs',
                  'pre_event',
                  'background',
                  'b_title',
                  ]

        widgets = {'accepted': HiddenInput(),
                   'submitted': HiddenInput(),
                   'b_title': HiddenInput(),
                   'b_description': HiddenInput(),
                   'profile': HiddenInput()}
        labels = volunteer_labels
        help_texts = volunteer_help_texts
