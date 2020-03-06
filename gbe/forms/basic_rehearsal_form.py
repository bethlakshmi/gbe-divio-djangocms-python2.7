from django.forms import (
    CharField,
    ChoiceField,
    HiddenInput,
    Form,
)


class BasicRehearsalForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    booking_id = CharField(widget=HiddenInput, required=False)
    rehearsal = ChoiceField()

    def __init__(self, *args, **kwargs):
        super(BasicRehearsalForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['booking_id', 'rehearsal']
