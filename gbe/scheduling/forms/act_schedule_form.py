from django.forms import (
    CharField,
    ChoiceField,
    Form,
    HiddenInput,
    IntegerField,
    NumberInput,
    TextInput,
)
from django.core.validators import MinValueValidator


class ActScheduleBasics(Form):
    '''
    Presents an act for scheduling as one line on a multi-line form.
    '''
    order = IntegerField(validators=[MinValueValidator(0)],
                         widget=NumberInput(attrs={'style': 'width: 3.5em'}))


class ActScheduleForm(Form):
    '''
    Presents an act for scheduling as one line on a multi-line form.
    '''
    performer = CharField(
        widget=TextInput(attrs={'readonly': 'readonly'}))
    title = CharField(
        widget=TextInput(attrs={'readonly': 'readonly'}))
    booking_id = CharField(widget=HiddenInput)
    show = ChoiceField(choices=[])
    order = IntegerField()

    def __init__(self, *args, **kwargs):
        show_choices = []
        if 'show_choices' in kwargs:
            show_choices = kwargs.pop('show_choices')
        super(ActScheduleForm, self).__init__(*args, **kwargs)
        self.fields['show'].choices = show_choices
