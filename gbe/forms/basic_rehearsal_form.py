from django.forms import (
    ChoiceField,
    HiddenInput,
    IntegerField,
    Form,
)


class BasicRehearsalForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    show_private = IntegerField(widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        super(BasicRehearsalForm, self).__init__(*args, **kwargs)
        if 'rehearsal' in kwargs['initial']:
            self.fields['rehearsal'] = ChoiceField(
                choices=kwargs['initial']['rehearsal_choices'],
                initial=kwargs['initial']['rehearsal'],
                label=kwargs['initial']['rehearsal_label'])
        else:
            self.fields['rehearsal'] = ChoiceField(
                choices=kwargs['initial']['rehearsal_choices'],
                label=kwargs['initial']['rehearsal_label'])

    class Meta:
        fields = ['show_private', 'rehearsal']
