from django.forms import (
    DecimalField,
    ModelForm,
)
from gbe.models import (
    StyleVersion,
)


class ThemeVersionForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    number = DecimalField(initial=1.0, label="Version Number", min_value=0.1)

    class Meta:
        model = StyleVersion
        fields = ['name', 'number']
