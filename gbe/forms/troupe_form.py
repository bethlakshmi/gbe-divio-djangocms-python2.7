from django.forms import (
    ModelMultipleChoiceField,
)
from gbe.models import Troupe
from gbe_forms_text import (
    persona_help_texts,
    persona_labels,
)
from gbe.forms.common_queries import visible_personas
from gbe.forms import PersonaForm


class TroupeForm(PersonaForm):
    required_css_class = 'required'
    error_css_class = 'error'
    membership = ModelMultipleChoiceField(
        queryset=visible_personas)

    class Meta:
        model = Troupe
        fields = ['contact',
                  'name',
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
