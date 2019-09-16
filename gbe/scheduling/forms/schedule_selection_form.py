from django.forms import (
    CharField,
    ModelChoiceField,
    ModelMultipleChoiceField,
    TextInput,
)
from gbe.models import (
    Event,
)
from gbe_forms_text import (
    scheduling_help_texts,
    scheduling_labels,
)
from gbe.forms.common_queries import (
    visible_personas,
    visible_profiles,
)
from gbe.scheduling.forms import ScheduleBasicForm
from tinymce.widgets import TinyMCE


class ScheduleSelectionForm(ScheduleBasicForm):
    e_title = CharField(
        widget=TextInput(attrs={'size': '79'}),
        label=scheduling_labels['e_title'],
        help_text=scheduling_help_texts['e_title'])

    e_description = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        label=scheduling_labels['e_description'],
        help_text=scheduling_help_texts['e_description'])
    teacher = ModelChoiceField(
        queryset=visible_personas,
        required=False)
    moderator = ModelChoiceField(
        queryset=visible_personas,
        required=False)
    panelists = ModelMultipleChoiceField(
        queryset=visible_personas,
        required=False)
    staff_lead = ModelChoiceField(
        queryset=visible_profiles,
        required=False)

    class Meta:
        model = Event
        fields = ['e_title', 'e_description', 'duration']
        help_texts = scheduling_help_texts
        labels = scheduling_labels
