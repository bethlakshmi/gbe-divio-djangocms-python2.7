from django.forms.fields import CharField
from django.forms.utils import ValidationError as FormValidationError
from django.forms.widgets import URLInput
from datetime import timedelta
from duration import Duration


class FriendlyURLInput(URLInput):
    input_type = 'text'
    pattern = "(https?://)?\w(\.\w+?)+(/~?\w+)?"
