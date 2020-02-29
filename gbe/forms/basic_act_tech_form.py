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
    confirm_no_music = TypedChoiceField(
        choices=((0, 'Yes, I will upload an audio track'),
                 (1, 'No, I will not need an audio track')),
        coerce=int)
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
                  'track',
                  'confirm_no_music',
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

    def clean(self):
        # run the parent validation first
        cleaned_data = super(BasicActTechForm, self).clean()

        # doing is_complete doesn't work, that executes the pre-existing
        # instance, not the current data

        if not (cleaned_data.get("confirm_no_music") or (
                cleaned_data.get("track_title") and 
                cleaned_data.get("track_title") and 
                cleaned_data.get("track"))):
            error = ValidationError((
                'Incomplete Audio Info - please either provide Track ' \
                'Title, Artist and the audio file, or confirm that ' \
                'there is no music.'),
                code='invalid')
            self.add_error('confirm_no_music', error)

        return cleaned_data
