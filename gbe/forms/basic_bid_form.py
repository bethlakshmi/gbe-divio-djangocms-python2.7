from django.forms import (
    CharField,
    Form,
)
from gbe_forms_text import (
    participant_form_help_texts,
    participant_labels,
)


class BasicBidForm(Form):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'

    phone = CharField(required=True,
                      help_text=participant_form_help_texts['phone'])
    first_name = CharField(
        required=True,
        label=participant_labels['legal_first_name'])
    last_name = CharField(
        required=True,
        label=participant_labels['legal_last_name'],
        help_text=participant_form_help_texts['legal_name'])

    class Meta:
        fields = ['first_name',
                  'last_name',
                  'phone']
