from django.forms import (
    ChoiceField,
    HiddenInput,
    ModelForm,
)
from gbe.models import VolunteerInterest
from gbe_forms_text import (
    rank_interest_options,
)


class VolunteerInterestForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super(VolunteerInterestForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            self.fields['rank'] = ChoiceField(
                choices=rank_interest_options,
                label=initial['interest'].interest,
                help_text=initial['interest'].help_text,
                required=False)

    class Meta:
        model = VolunteerInterest
        fields = ['rank',
                  'interest']
        widgets = {'interest': HiddenInput()}
