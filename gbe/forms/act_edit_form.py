from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    HiddenInput,
    ModelForm,
    MultipleChoiceField,
    Textarea,
    TextInput,
    URLField,
    URLInput,
)
from gbe.models import Act
from gbe_forms_text import (
    act_help_texts,
    act_bid_labels,
)
from gbetext import (
    act_other_perf_options,
    act_shows_options,
)
from gbe.expoformfields import (
    DurationFormField,
)


class ActEditDraftForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['act_duration']
    )
    track_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['track_duration'],
        label=act_bid_labels['track_duration']
    )
    track_artist = CharField(required=False)
    track_title = CharField(required=False)
    shows_preferences = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=act_shows_options,
        label=act_bid_labels['shows_preferences'],
        help_text=act_help_texts['shows_preferences'],
        required=False
    )
    other_performance = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=act_other_perf_options,
        label=act_bid_labels['other_performance'],
        help_text=act_help_texts['other_performance'],
        required=False
    )
    video_link = URLField(
        widget=URLInput(attrs={'placeholder': 'http://'}),
        help_text=act_help_texts['video_link'],
        label=act_bid_labels['video_link'],
        required=False
    )
    b_conference = HiddenInput()

    class Meta:
        model = Act
        fields = [
            'performer',
            'shows_preferences',
            'other_performance',
            'b_title',
            'track_title',
            'track_artist',
            'track_duration',
            'act_duration',
            'video_link',
            'video_choice',
            'b_description',
            'why_you',
            'b_conference',
            'act_duration',
            'track_duration',
            'track_artist',
            'track_title']
        labels = act_bid_labels
        help_texts = act_help_texts
        widgets = {'b_conference': HiddenInput()}


class ActEditForm(ActEditDraftForm):
    act_duration = DurationFormField(
        required=True,
        help_text=act_help_texts['act_duration']
    )
    shows_preferences = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=act_shows_options,
        label=act_bid_labels['shows_preferences'],
        help_text=act_help_texts['shows_preferences']
    )
    b_description = CharField(
        required=True,
        label=act_bid_labels['description'],
        help_text=act_help_texts['description'],
        widget=Textarea)
