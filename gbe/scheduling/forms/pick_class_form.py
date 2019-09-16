from django.forms import (
    ModelChoiceField,
    Form,
    RadioSelect,
)
from gbe.models import Class


class PickClassField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s - %s" % (obj.b_title, obj.teacher)


class PickClassForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    accepted_class = PickClassField(
        queryset=Class.objects.filter(accepted=3).order_by('b_title'),
        widget=RadioSelect,
        empty_label="Make New Class",
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super(PickClassForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            self.fields['accepted_class'].queryset = Class.objects.filter(
                b_conference=initial['conference'],
                accepted=3).order_by('b_title')
