from django.forms import (
    CharField,
    ModelForm,
)
from gbe.models import Profile
from gbe_forms_text import (
    participant_form_help_texts,
    participant_labels,
)


class InvolvedProfileForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    first_name = CharField(
        required=True,
        label=participant_labels['legal_first_name'])
    last_name = CharField(
        required=True,
        label=participant_labels['legal_last_name'],
        help_text=participant_form_help_texts['legal_name'])
    phone = CharField(required=True)

    def save(self, commit=True):
        form = super(InvolvedProfileForm, self).save(commit=False)
        if not self.is_valid():
            return
        form.user_object.first_name = self.cleaned_data['first_name'].strip()
        form.user_object.last_name = self.cleaned_data['last_name'].strip()
        if commit and self.is_valid():
            form.save()
            form.user_object.save()

    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = ['first_name',
                  'last_name',
                  'phone',
                  ]
        labels = participant_labels
        help_texts = participant_form_help_texts
