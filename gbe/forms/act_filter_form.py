from django.forms import (
    CheckboxSelectMultiple,
    Form,
    MultipleChoiceField,
)
from gbetext import act_shows_options_short


class ActFilterForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    shows_preferences = MultipleChoiceField(
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        choices=act_shows_options_short,
        label="Preferred Shows",
        required=False
    )
