from django.forms import (
    CharField,
    ChoiceField,
    HiddenInput,
    IntegerField,
    Form,
    TextInput,
)


class RehearsalSelectionForm(Form):
    show = CharField(widget=TextInput(
        attrs={'readonly': 'readonly'})
    )
    show_private = IntegerField(widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        super(RehearsalSelectionForm, self).__init__(*args, **kwargs)
        if 'rehearsal' in kwargs['initial']:
            self.fields['rehearsal'] = ChoiceField(
                choices=kwargs['initial']['rehearsal_choices'],
                initial=kwargs['initial']['rehearsal'])
        else:
            self.fields['rehearsal'] = ChoiceField(
                choices=kwargs['initial']['rehearsal_choices'])

    class Meta:
        fields = ['show_private', 'show', 'rehearsal']
