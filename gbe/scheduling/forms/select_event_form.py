from django.forms import (
    Form,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import calendar_type as calendar_type_options
from gbe_forms_text import event_type_options
from gbe.models import StaffArea
from django.db.models.functions import Lower


class SelectEventForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    day = MultipleChoiceField(
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False)
    calendar_type = MultipleChoiceField(
        choices=list(calendar_type_options.items()),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False)
    event_style = MultipleChoiceField(
        choices=list(event_type_options),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False)
    staff_area = ModelMultipleChoiceField(
        queryset=StaffArea.objects.all().order_by("conference", "slug"),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False)


class HiddenSelectEventForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    day = MultipleChoiceField(
        widget=MultipleHiddenInput(),
        required=False)
    calendar_type = MultipleChoiceField(
        choices=list(calendar_type_options.items()),
        widget=MultipleHiddenInput(),
        required=False)
    event_style = MultipleChoiceField(
        choices=list(event_type_options),
        widget=MultipleHiddenInput(),
        required=False)
    staff_area = ModelMultipleChoiceField(
        queryset=StaffArea.objects.all().order_by("conference", "slug"),
        widget=MultipleHiddenInput(),
        required=False)
