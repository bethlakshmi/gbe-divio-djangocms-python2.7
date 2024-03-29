from django.forms import (
    CharField,
    Form,
    SlugField,
    Textarea,
)
from gbe_forms_text import event_help_texts


class EventBookingForm(Form):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    title = CharField()
    description = CharField(
        widget=Textarea(attrs={'id': 'admin-tiny-mce'}))
    slug = SlugField(help_text=event_help_texts['slug'],
                     required=False)

    class Meta:
        fields = [
            'title',
            'slug',
            'description']
        help_texts = event_help_texts
