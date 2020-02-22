from django.forms import (
    CharField,
    EmailField,
    Form,
    MultipleChoiceField,
    Textarea,
    TextInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.html import strip_tags


class AdHocEmailForm(Form):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    to = MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    sender = EmailField(required=True,
                        label="From")
    subject = CharField(widget=TextInput(attrs={'size': '79'}))
    html_message = CharField(
        widget=Textarea(attrs={'id': 'admin-tiny-mce'}),
        label="Message")
