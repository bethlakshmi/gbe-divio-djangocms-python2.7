from django.forms import (
    CharField,
    ModelForm,
    HiddenInput,
    ModelChoiceField,
)
from gbe.models import StaffArea
from tinymce.widgets import TinyMCE
from gbe.forms.common_queries import visible_profiles

class StaffAreaForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    description = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}))
    staff_lead = ModelChoiceField(
        queryset=visible_profiles,
        required=False)

    class Meta:
        model = StaffArea
        fields = '__all__'
        widgets = {'conference': HiddenInput()}
