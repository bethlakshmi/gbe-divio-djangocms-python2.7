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
from gbe_forms_text import sender_name_help


class AdHocEmailForm(Form):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    to = MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    sender = EmailField(required=True,
                        label="From")
    sender_name = CharField(max_length=150,
                            required=True,
                            help_text=sender_name_help)
    subject = CharField(widget=TextInput(attrs={'size': '79'}))
    html_message = CharField(
        widget=Textarea(attrs={'id': 'admin-tiny-mce'}),
        label="Message")
