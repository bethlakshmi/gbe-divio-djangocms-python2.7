from django.forms import (
    ChoiceField,
    ModelForm,
    MultipleChoiceField,
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

class BasicActTechForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    starting_position = ChoiceField(
        choices=starting_position_choices)
    prop_setup = MultipleChoiceField(
        choices=prop_choices,
        widget=CheckboxSelectMultiple(),
        error_messages={'required': 'Please select at least one option'},
        label=tech_labels['prop_setup']
        )
    follow_spot = TypedChoiceField(
        choices=((False, 'No'), (True, 'Yes')))

    class Meta:
        model = TechInfo
        labels = tech_labels
        help_texts = tech_help_texts
        fields = ['track_title',
                  'track_artist',
                  'duration',
                  'prop_setup',
                  'crew_instruct',
                  'introduction_text',
                  'read_exact',
                  'pronouns',
                  'feel_of_act',
                  'primary_color',
                  'secondary_color',
                  'follow_spot',
                  'starting_position']
