from django.forms import (
    HiddenInput,
    ModelForm,
)
from gbe.models import ConferenceVolunteer


class ConferenceVolunteerForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = ConferenceVolunteer
        fields, required = ConferenceVolunteer().bid_fields
        widgets = {'bid': HiddenInput()}
