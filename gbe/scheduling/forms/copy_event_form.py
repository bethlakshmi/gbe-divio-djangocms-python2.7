from django.forms import (
    IntegerField,
    HiddenInput,
    ModelChoiceField,
    MultipleChoiceField,
    Form,
    CheckboxSelectMultiple,
    ChoiceField,
)
from gbe_forms_text import (
    copy_mode_labels,
    copy_mode_choices,
)
from gbe.models import (
    Event,
    ConferenceDay,
)


class CopyEventForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    copied_event = MultipleChoiceField(
        choices=(),
        widget=CheckboxSelectMultiple(attrs={"checked": ""}),
        label='',
        required=False,
        )

    copy_mode = ChoiceField(choices=copy_mode_choices,
                            required=False,
                            widget=HiddenInput)

    target_event = IntegerField(
        required=False,
        widget=HiddenInput)

    copy_to_day = ModelChoiceField(
        queryset=ConferenceDay.objects.exclude(
            conference__status="completed").order_by('day'),
        required=False,
        widget=HiddenInput)
