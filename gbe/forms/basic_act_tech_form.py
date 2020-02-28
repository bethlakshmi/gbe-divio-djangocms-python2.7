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
    primary_color = CharField(label=tech_labels['primary_color'],
                              required=True)
    feel_of_act = CharField(label=tech_labels['feel_of_act'],
                            help_text=tech_help_texts['feel_of_act'],
                            required=True,
                            widget=Textarea)
    pronouns = CharField(label=tech_labels['pronouns'],
                         required=True)
    introduction_text = CharField(
      label=tech_labels['introduction_text'],
      help_text=tech_help_texts['introduction_text'],
      required=True,
      widget=Textarea)

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
