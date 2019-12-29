from django.forms import ModelForm
from gbe.models import ProfilePreferences
from gbe_forms_text import (
    profile_preferences_help_texts,
    profile_preferences_labels,
)


class EmailPreferencesForm(ModelForm):
    class Meta:
        model = ProfilePreferences
        fields = ['send_daily_schedule',
                  'send_bid_notifications',
                  'send_role_notifications',
                  'send_schedule_change_notifications']
        help_texts = profile_preferences_help_texts
        labels = profile_preferences_labels
