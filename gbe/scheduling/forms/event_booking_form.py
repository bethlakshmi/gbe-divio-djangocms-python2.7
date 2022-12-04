from django.forms import (
    CharField,
    ModelForm,
    SlugField,
    Textarea,
)
from gbe.models import Event
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)


class EventBookingForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    e_description = CharField(
        widget=Textarea(attrs={'id': 'admin-tiny-mce'}),
        label=event_labels['e_description'])
    slug = SlugField(help_text=event_help_texts['slug'],
                     required=False)

    class Meta:
        model = Event
        fields = [
            'e_title',
            'slug',
            'e_description']
        help_texts = event_help_texts
        labels = event_labels
