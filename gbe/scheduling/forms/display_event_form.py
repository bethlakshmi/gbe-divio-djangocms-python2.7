from django.forms import (
    Form,
    ModelMultipleChoiceField,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbe.models import StaffArea


class DisplayEventForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    staff_area = ModelMultipleChoiceField(
        queryset=StaffArea.objects.all().order_by("conference", "slug"),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False)
