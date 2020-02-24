from django.forms import (
    Form,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from gbe.models import (
    Event,
    StaffArea,
)
from gbe_forms_text import event_collect_choices


class SelectEventForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    events = ModelMultipleChoiceField(
        queryset=Event.objects.all(),
        widget=MultipleHiddenInput(),
        required=False)
    staff_areas = ModelMultipleChoiceField(
        queryset=StaffArea.objects.all(),
        widget=MultipleHiddenInput(),
        required=False)
    event_collections = MultipleChoiceField(
        required=False,
        widget=MultipleHiddenInput(),
        choices=event_collect_choices)
