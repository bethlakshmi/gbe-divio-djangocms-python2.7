from django.forms import HiddenInput
from gbe_forms_text import event_help_texts
from gbe.scheduling.forms import EventBookingForm


class GenericBookingForm(EventBookingForm):
    class Meta:
        fields = [
            'title',
            'slug',
            'description',
            'type',
            'conference', ]
        help_texts = event_help_texts
        widgets = {'type': HiddenInput(),
                   'conference': HiddenInput()}
