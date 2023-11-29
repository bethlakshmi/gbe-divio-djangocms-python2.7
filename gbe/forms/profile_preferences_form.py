from django.forms import ModelForm
from gbe.models import ProfilePreferences
from gbe_forms_text import (
    profile_preferences_help_texts,
    profile_preferences_labels,
)


class ProfilePreferencesForm(ModelForm):
    class Meta:
        model = ProfilePreferences
        fields = ['in_hotel']
        help_texts = profile_preferences_help_texts
        labels = profile_preferences_labels
