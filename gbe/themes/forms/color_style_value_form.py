from django.forms import (
    CharField,
    HiddenInput,
    ModelChoiceField,
    ModelForm,
    TextInput,
)
from gbe.models import (
    StyleProperty,
    StyleValue,
)


class ColorStyleValueForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    value = CharField(widget=TextInput(attrs={'data-jscolor': ''}))
    style_property = ModelChoiceField(widget=HiddenInput(),
                                      queryset=StyleProperty.objects.all())

    class Meta:
        model = StyleValue
        fields = ['value', 'style_property']
