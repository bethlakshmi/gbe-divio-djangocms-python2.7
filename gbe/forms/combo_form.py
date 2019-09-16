from django.forms import (
    ModelForm,
)
from gbe.models import Combo


class ComboForm (ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Combo
        fields = ['contact', 'name', 'membership']
