from django.forms import (
    CharField,
    ModelForm,
    Textarea,
)
from gbe.models import Event
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)


class EventBookingForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    e_description = CharField(
        widget=Textarea(attrs={'id': 'admin-tiny-mce'}),
        label=event_labels['e_description'])

    class Meta:
        model = Event
        fields = [
            'e_title',
            'e_description']
        help_texts = event_help_texts
        labels = event_labels
