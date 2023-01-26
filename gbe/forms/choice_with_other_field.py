from django.forms import (
    CharField,
    ChoiceField,
    MultiValueField,
    MultiWidget,
    RadioSelect,
    TextInput,
    ValidationError
)


class ChoiceWithOtherWidget(MultiWidget):
    '''MultiWidget for use with ChoiceWithOtherField.'''
    template_name = 'gbe/choice_with_other_widget.tmpl'

    def __init__(self, choices):
        widgets = [RadioSelect(choices=choices), TextInput()]
        super(ChoiceWithOtherWidget, self).__init__(widgets)

    def decompress(self, value):
        ''' Fill form with value - if it's in the choice set, the right
            choice is set.  Else, the choice is the last one and box gets the
            data
        '''
        if not value:
            return [None, None]
        for choice, display in self.widgets[0].choices:
            if choice == value:
                return [value, None]
        return ['', value]


class ChoiceWithOtherField(MultiValueField):
    ''' Given a list of choices, this sets up a set of radio buttons and
        a text box on the last line for "other" entries.
        Requires a list of choices with the last one being an empty string
        value.
        Returns a single string - either one of the first n-1 choices, or
        the value of the text box if other is chosen.
    '''
    def __init__(self, *args, **kwargs):
        self._was_required = kwargs.pop('required', True)
        fields = [
            ChoiceField(widget=RadioSelect, required=False, *args, **kwargs),
            CharField(required=False)
        ]
        widget = ChoiceWithOtherWidget(choices=kwargs['choices'])
        kwargs.pop('choices')
        kwargs['required'] = self._was_required
        super().__init__(widget=widget,
                         fields=fields,
                         require_all_fields=False,
                         *args,
                         **kwargs)

    def compress(self, value):
        ''' Verify form post and present data - returns either one of the
            first n-1 values or if the last is chosen, the text field.
            If it's a required field - one of the two must be chosen.
        '''
        if self._was_required and not value or (
                value[0] in (None, '') and value[1] in (None, '')):
            raise ValidationError(self.error_messages['required'])

        if not value:
            return None
        if value[0] == '':
            return value[1]
        else:
            return value[0]
