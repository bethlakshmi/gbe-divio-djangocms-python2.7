from django.forms import (
    CharField,
    ChoiceField,
    HiddenInput,
    IntegerField,
    Form,
    ModelChoiceField,
)
from gbe.models import GenericEvent
from gbe.forms.common_queries import visible_profiles
from gbetext import role_options
from dal import autocomplete


class WorkerAllocationForm(Form):
    '''
    Form for selecting a worker to fill a slot in a Volunteer Opportunity
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    worker = ModelChoiceField(
        queryset=visible_profiles,
        required=False,
        widget=autocomplete.ModelSelect2(
            url='profile-autocomplete'))
    role = ChoiceField(choices=role_options, initial='Volunteer')
    label = CharField(max_length=100, required=False)
    alloc_id = IntegerField(required=False, widget=HiddenInput())

    def __init__(self, *args, **kwargs):
        super(WorkerAllocationForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            if 'worker' in initial:
                self.fields['worker'].widget.attrs = {
                    "id": initial['worker'].pk}
