from django.forms import (
    HiddenInput,
    IntegerField,
    ModelChoiceField,
    MultipleChoiceField,
)
from gbe.models import (
    Account,
    Bio,
)
from gbe_forms_text import (
    persona_help_texts,
    troupe_labels,
)
from gbe.forms import PersonaForm
from dal import autocomplete
from django.urls import reverse_lazy
from gbe.forms.common_queries import visible_profiles


class TroupeForm(PersonaForm):
    required_css_class = 'required'
    error_css_class = 'error'
    contact = ModelChoiceField(
        queryset=Account.objects.all(),
        empty_label=None,
        label=troupe_labels['contact'])
    year_started = IntegerField(
        required=True,
        label=troupe_labels['year_started'],
        help_text=persona_help_texts['year_started'])

    membership = MultipleChoiceField(widget=autocomplete.ModelSelect2Multiple(
        url=reverse_lazy('profile-autocomplete', urlconf='gbe.urls')))

    def clean(self):
        cleaned_data = super(TroupeForm, self).clean()
        if 'name' in cleaned_data:
            cleaned_data['name'] = cleaned_data['name'].strip('\'\"')
        return cleaned_data

    class Meta:
        model = Bio
        fields = ['contact',
                  'name',
                  'label',
                  'pronouns',
                  'bio',
                  'year_started',
                  'awards',
                  'upload_img',
                  'festivals',
                  'multiple_performers',
                  ]
        help_texts = persona_help_texts
        labels = troupe_labels
        widgets = {'multiple_performers': HiddenInput()}
