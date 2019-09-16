from django.forms import (
    CheckboxSelectMultiple,
    ModelForm,
    MultipleChoiceField,
)
from gbe.models import ProfilePreferences
from gbe_forms_text import (
    inform_about_options,
    profile_preferences_help_texts,
    profile_preferences_labels,
)


class ProfilePreferencesForm(ModelForm):
    inform_about = MultipleChoiceField(
        choices=inform_about_options,
        required=False,
        widget=CheckboxSelectMultiple(),
        label=profile_preferences_labels['inform_about'])

    class Meta:
        model = ProfilePreferences
        fields = ['inform_about', 'in_hotel', 'show_hotel_infobox']
        help_texts = profile_preferences_help_texts
        labels = profile_preferences_labels
