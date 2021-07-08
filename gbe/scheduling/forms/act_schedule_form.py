from django.forms import (
    Form,
    IntegerField,
    NumberInput,
)
from django.core.validators import MinValueValidator


class ActScheduleBasics(Form):
    '''
    Presents an act for scheduling as one line on a multi-line form.
    '''
    order = IntegerField(validators=[MinValueValidator(0)],
                         widget=NumberInput(attrs={'style': 'width: 3.5em'}))
