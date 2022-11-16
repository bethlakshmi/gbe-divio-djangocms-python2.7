from django.forms import HiddenInput
from gbe.models import GenericEvent
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from gbe.scheduling.forms import EventBookingForm


class GenericBookingForm(EventBookingForm):
    class Meta:
        model = GenericEvent
        fields = [
            'e_title',
            'e_description',
            'type',
            'e_conference', ]
        help_texts = event_help_texts
        labels = event_labels
        widgets = {'type': HiddenInput(),
                   'e_conference': HiddenInput()}
