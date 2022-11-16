from django.forms import HiddenInput
from gbe.models import Show
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from gbe.scheduling.forms import EventBookingForm


class ShowBookingForm(EventBookingForm):
    class Meta:
        model = Show
        fields = [
            'e_title',
            'slug',
            'e_description',
            'e_conference', ]
        help_texts = event_help_texts
        labels = event_labels
        widgets = {'e_conference': HiddenInput()}
