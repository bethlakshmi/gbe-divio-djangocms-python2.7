from django.forms import ModelForm
from gbe_forms_text import (
    tech_labels,
    tech_help_texts,
)
from gbe.models import TechInfo


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
