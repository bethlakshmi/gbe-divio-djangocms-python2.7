from django.forms import (
    ModelForm,
)
from gbe.models import LightingInfo
from gbe_forms_text import (
    lighting_help_texts,
    lighting_labels,
)


class LightingInfoForm(ModelForm):
    form_title = "Lighting Info"

    class Meta:
        model = LightingInfo
        labels = lighting_labels
        help_texts = lighting_help_texts
        fields = '__all__'
