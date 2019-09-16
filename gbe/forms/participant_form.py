from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    EmailField,
    ModelForm,
    MultipleChoiceField,
)
from gbe.models import Profile
from gbe_forms_text import (
    how_heard_options,
    participant_form_help_texts,
    participant_labels,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import re


class ParticipantForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = EmailField(required=True)
    first_name = CharField(
        required=True,
        label=participant_labels['legal_first_name'],
        help_text=participant_form_help_texts['legal_name'])
    last_name = CharField(
        required=True,
        label=participant_labels['legal_last_name'],
        help_text=participant_form_help_texts['legal_name'])
    phone = CharField(required=True)

    how_heard = MultipleChoiceField(
        choices=how_heard_options,
        required=False,
        widget=CheckboxSelectMultiple(),
        label=participant_labels['how_heard'])

    def clean(self):
        changed = self.changed_data
        if self.has_changed() and 'email' in self.changed_data:
            if User.objects.filter(
                    email=self.cleaned_data.get('email')).exists():
                raise ValidationError('That email address is already in use')
        return self.cleaned_data

    def save(self, commit=True):
        partform = super(ParticipantForm, self).save(commit=False)
        user = partform.user_object
        if not self.is_valid():
            return
        partform.user_object.email = self.cleaned_data.get('email')
        if len(self.cleaned_data['first_name'].strip()) > 0:
            user.first_name = self.cleaned_data['first_name'].strip()
        if len(self.cleaned_data['last_name'].strip()) > 0:
            user.last_name = self.cleaned_data['last_name'].strip()
        if self.cleaned_data['display_name']:
            display_name = self.cleaned_data['display_name'].strip()
        else:
            display_name = "%s %s" % (user.first_name, user.last_name)
        partform.display_name = re.sub(' +', ' ', display_name).title()

        if commit and self.is_valid():
            partform.save()
            partform.user_object.save()

    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = ['first_name',
                  'last_name',
                  'display_name',
                  'email',
                  'address1',
                  'address2',
                  'city',
                  'state',
                  'zip_code',
                  'country',
                  'phone',
                  'best_time',
                  'how_heard',
                  ]
        labels = participant_labels
        help_texts = participant_form_help_texts
