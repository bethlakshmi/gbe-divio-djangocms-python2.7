from django.forms import (
    CharField,
    ModelForm,
    HiddenInput,
    ModelChoiceField,
    Textarea,
)
from gbe.models import (
    Room,
    StaffArea,
)
from gbe.forms.common_queries import visible_profiles


class StaffAreaForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    description = CharField(
        widget=Textarea(attrs={'id': 'admin-tiny-mce'}))
    staff_lead = ModelChoiceField(
        queryset=visible_profiles,
        required=False)

    class Meta:
        model = StaffArea
        fields = '__all__'
        widgets = {'conference': HiddenInput()}

    def __init__(self, *args, **kwargs):
        super(StaffAreaForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['default_location'].queryset = Room.objects.filter(
                conferences=kwargs.get('instance').conference)
        elif 'initial' in kwargs:
            initial = kwargs.pop('initial')
            self.fields['default_location'].queryset = Room.objects.filter(
                conferences=initial['conference'])
