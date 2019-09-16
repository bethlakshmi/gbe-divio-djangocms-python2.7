from django.forms import (
    BooleanField,
    CheckboxSelectMultiple,
    HiddenInput,
    MultipleChoiceField,
)
from gbe.forms import (
    ActEditDraftForm,
    ActEditForm,
)
from gbe_forms_text import (
    act_help_texts,
    act_bid_labels,
    also_consider_act_for,
    summer_bid_label,
    summer_help_texts,
)
from gbetext import (
    more_shows_options,
    summer_other_perf_options,
)
from gbe.functions import get_current_conference
from gbe.expoformfields import (
    DurationFormField,
)
from gbe.models import Act


class SummerActDraftForm(ActEditDraftForm):
    shows_preferences = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=more_shows_options,
        label=summer_bid_label,
        help_text=summer_help_texts['shows_preferences'],
        required=False
    )
    other_performance = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=summer_other_perf_options,
        label=act_bid_labels['other_performance'],
        help_text=act_help_texts['other_performance'],
        required=False
    )
    act_duration = DurationFormField(
        required=False,
        help_text=summer_help_texts['act_duration']
    )
    track_duration = DurationFormField(
        required=False,
        help_text=summer_help_texts['track_duration'],
        label=act_bid_labels['track_duration']
    )


class SummerActForm(SummerActDraftForm):
    shows_preferences = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=more_shows_options,
        label=act_bid_labels['summer_shows_preferences'],
        help_text=act_help_texts['shows_preferences']
    )

    act_duration = DurationFormField(
        required=True,
        help_text=summer_help_texts['act_duration']
    )
