from django.forms import (
    ChoiceField,
    Form,
    RadioSelect,
)
from gbe_forms_text import event_type_options


class PickEventForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    event_type = ChoiceField(choices=event_type_options, widget=RadioSelect)
