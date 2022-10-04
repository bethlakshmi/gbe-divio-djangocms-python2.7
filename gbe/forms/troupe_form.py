from django.forms import (
    IntegerField,
    ModelChoiceField,
    ModelMultipleChoiceField,
)
from gbe.models import (
    Profile,
    Troupe,
)
from gbe_forms_text import (
    persona_help_texts,
    troupe_labels,
)
from gbe.forms import PersonaForm
from dal import autocomplete


class TroupeForm(PersonaForm):
    required_css_class = 'required'
    error_css_class = 'error'
    contact = ModelChoiceField(
        queryset=Profile.objects.all(),
        empty_label=None,
        label=troupe_labels['contact'])
    year_started = IntegerField(
        required=True,
        label=troupe_labels['year_started'],
        help_text=persona_help_texts['year_started'])

    def clean(self):
        cleaned_data = super(TroupeForm, self).clean()
        if 'name' in cleaned_data:
            cleaned_data['name'] = cleaned_data['name'].strip('\'\"')
        return cleaned_data


    class Meta:
        model = Troupe
        fields = ['contact',
                  'name',
                  'label',
                  'membership',
                  'homepage',
                  'bio',
                  'year_started',
                  'awards',
                  'upload_img',
                  'festivals',
                  ]
        help_texts = persona_help_texts
        labels = troupe_labels
        widgets = {
            'membership': autocomplete.ModelSelect2Multiple(
                url='persona-autocomplete')}
