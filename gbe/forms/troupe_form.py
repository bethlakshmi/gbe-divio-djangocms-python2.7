from django.forms import (
    ModelMultipleChoiceField,
)
from gbe.models import Troupe
from gbe_forms_text import (
    persona_help_texts,
    persona_labels,
)
from gbe.forms import PersonaForm
from dal import autocomplete


class TroupeForm(PersonaForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Troupe
        fields = ['contact',
                  'name',
                  'label',
                  'homepage',
                  'bio',
                  'experience',
                  'awards',
                  'upload_img',
                  'festivals',
                  'membership',
                  ]
        help_texts = persona_help_texts
        labels = persona_labels
        widgets = {
            'membership': autocomplete.ModelSelect2Multiple(
                url='persona-autocomplete')}
