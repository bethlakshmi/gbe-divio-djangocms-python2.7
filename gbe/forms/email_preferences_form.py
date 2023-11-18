from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    HiddenInput,
    ModelForm,
    MultipleChoiceField,
)
from gbe.models import ProfilePreferences
from gbe_forms_text import (
    inform_about_options,
    profile_preferences_help_texts,
    profile_preferences_labels,
)
from django.utils.safestring import mark_safe
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget


class EmailPreferencesForm(ModelForm):
    inform_about = MultipleChoiceField(
        choices=inform_about_options,
        required=False,
        widget=CheckboxSelectMultiple(),
        label=profile_preferences_labels['inform_about'])

    def __init__(self, *args, **kwargs):
        interest_disable = []
        if 'interest_disable' in kwargs:
            interest_disable = kwargs.pop('interest_disable')
        if 'instance' in kwargs and kwargs.get('instance') is not None and (
                len(kwargs.get('instance').inform_about.strip()) > 0):
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial']['inform_about'] = []
            for interest in eval(kwargs.get('instance').inform_about):
                if interest not in interest_disable:
                    kwargs['initial']['inform_about'] += [interest]

        super(EmailPreferencesForm, self).__init__(*args, **kwargs)
        inform_choices = []
        for choice in inform_about_options:
            if choice[0] in interest_disable:
                inform_choices += [(choice[0], mark_safe(
                    ('<span class="font-weight-bold shadow-highlight">' +
                     '%s</span>') % (choice[1])))]
            else:
                inform_choices += [(choice[0], choice[1])]
        self.fields['inform_about'].choices = inform_choices

    class Meta:
        model = ProfilePreferences
        fields = ['send_daily_schedule',
                  'send_bid_notifications',
                  'send_role_notifications',
                  'send_schedule_change_notifications',
                  'inform_about']
        help_texts = profile_preferences_help_texts
        labels = profile_preferences_labels


class EmailPreferencesNoLoginForm(EmailPreferencesForm):
    token = CharField(widget=HiddenInput, required=True)
    verification = ReCaptchaField(widget=ReCaptchaWidget(), label="")
