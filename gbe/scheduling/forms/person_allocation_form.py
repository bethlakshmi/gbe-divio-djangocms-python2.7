from django.forms import (
    CharField,
    ChoiceField,
    HiddenInput,
    Form,
    ModelChoiceField,
    Select,
)
from gbetext import role_options
from dal import autocomplete
from gbe.forms.common_queries import (
    visible_personas,
    visible_profiles,
)


class PersonAllocationForm(Form):
    '''
    Form for selecting a worker to fill a slot in a Volunteer Opportunity
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    role = ChoiceField(choices=role_options, label="", widget=Select(
        attrs={'style': 'width:150px', }))
    worker = ModelChoiceField(
        queryset=visible_profiles,
        required=False,
        label="",
        widget=autocomplete.ModelSelect2(
                url='profile-autocomplete'))
    label = CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        label_visible = kwargs.pop('label_visible')
        role_options = kwargs.pop('role_options')
        use_personas = kwargs.pop('use_personas')

        super(PersonAllocationForm, self).__init__(*args, **kwargs)
        if not label_visible:
            self.fields['label'].widget = HiddenInput()

        self.fields['role'].choices = role_options

        if use_personas:
            self.fields['worker'].queryset = visible_personas
            self.fields['worker'].widget.url = 'persona-autocomplete'
