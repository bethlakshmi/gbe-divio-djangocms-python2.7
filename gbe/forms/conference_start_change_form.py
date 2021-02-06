from django.forms import (
    DateField,
    HiddenInput,
    ModelForm,
    NumberInput,
)
from tempus_dominus.widgets import DatePicker
from gbe.models import ConferenceDay


class ConferenceStartChangeForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    day = DateField(required=False, widget=DatePicker(
        attrs={
            'append': 'fa fa-calendar',
            'icon_toggle': True,
            },
        options={
            'format': "M/D/YYYY",
        }))

    class Meta:
        model = ConferenceDay
        fields = ['day']
