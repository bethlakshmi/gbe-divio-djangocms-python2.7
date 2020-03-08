from django.forms import (
    CharField,
    ChoiceField,
    ModelForm,
    MultipleChoiceField,
    Textarea,
    TypedChoiceField,
)
from gbe_forms_text import (
    prop_choices,
    starting_position_choices,
    tech_labels,
    tech_help_texts,
)
from gbe.models import TechInfo
from django.forms.widgets import CheckboxSelectMultiple
from django.core.exceptions import ValidationError


class AdvancedActTechForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = TechInfo
        labels = tech_labels
        help_texts = tech_help_texts
        fields = ['mic_choice',
                  'follow_spot_color',
                  'background_color',
                  'wash_color',
                  'special_lighting_cue',
                  'start_blackout',
                  'end_blackout']
