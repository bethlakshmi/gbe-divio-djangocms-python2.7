from django.forms import (
    ChoiceField,
    HiddenInput,
    IntegerField,
    Form,
)


class BasicRehearsalForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    booking_id = IntegerField(widget=HiddenInput, required=False)
    rehearsal = ChoiceField()

    def __init__(self, *args, **kwargs):
        super(BasicRehearsalForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['booking_id', 'rehearsal']
