from django.forms import (
    CheckboxSelectMultiple,
    HiddenInput,
    ModelForm,
    ModelMultipleChoiceField
)
from gbe.models import (
    Volunteer,
    VolunteerWindow,
)
from gbe_forms_text import (
    available_time_conflict,
    unavailable_time_conflict,
    volunteer_help_texts,
    volunteer_labels,
)


class VolunteerBidForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    b_title = HiddenInput()
    description = HiddenInput()
    available_windows = ModelMultipleChoiceField(
        queryset=VolunteerWindow.objects.none(),
        widget=CheckboxSelectMultiple,
        label=volunteer_labels['availability'],
        help_text=volunteer_help_texts['volunteer_availability_options'],
        required=True)
    unavailable_windows = ModelMultipleChoiceField(
        queryset=VolunteerWindow.objects.none(),
        widget=CheckboxSelectMultiple,
        label=volunteer_labels['unavailability'],
        help_text=volunteer_help_texts['volunteer_availability_options'],
        required=False)

    def __init__(self, *args, **kwargs):
        if 'available_windows' in kwargs:
            available_windows = kwargs.pop('available_windows')
        if 'unavailable_windows' in kwargs:
            unavailable_windows = kwargs.pop('unavailable_windows')
        super(VolunteerBidForm, self).__init__(*args, **kwargs)
        self.fields['available_windows'].queryset = available_windows
        self.fields['unavailable_windows'].queryset = unavailable_windows

    def clean(self):
        cleaned_data = super(VolunteerBidForm, self).clean()
        conflict_windows = []
        if ('available_windows' in self.cleaned_data) and (
                'unavailable_windows' in self.cleaned_data):
            conflict_windows = set(
                self.cleaned_data['available_windows']).intersection(
                self.cleaned_data['unavailable_windows'])
        if len(conflict_windows) > 0:
            windows = ", ".join(str(w) for w in conflict_windows)
            self._errors['available_windows'] = \
                available_time_conflict % windows
            self._errors['unavailable_windows'] = \
                unavailable_time_conflict
        return cleaned_data

    class Meta:
        model = Volunteer
        fields = ['number_shifts',
                  'available_windows',
                  'unavailable_windows',
                  'opt_outs',
                  'pre_event',
                  'background',
                  'b_title',
                  ]

        widgets = {'accepted': HiddenInput(),
                   'submitted': HiddenInput(),
                   'b_title': HiddenInput(),
                   'b_description': HiddenInput(),
                   'profile': HiddenInput()}
        labels = volunteer_labels
        help_texts = volunteer_help_texts
