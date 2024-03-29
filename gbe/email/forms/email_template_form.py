from django.forms import (
    CharField,
    HiddenInput,
    ModelForm,
    Textarea,
    TextInput,
)
from post_office.models import EmailTemplate
from django.utils.html import strip_tags
from gbe_forms_text import sender_name_help


class EmailTemplateForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    html_content = CharField(
        widget=Textarea(attrs={'id': 'admin-tiny-mce'}),
        label="Message")
    sender = CharField(max_length=100,
                       required=True,
                       label="From")
    sender_name = CharField(max_length=150,
                            required=True,
                            help_text=sender_name_help)
    subject = CharField(widget=TextInput(attrs={'size': '79'}))

    def save(self, commit=True):
        template = super(EmailTemplateForm, self).save(commit=False)
        template.content = strip_tags(self.cleaned_data['html_content'])
        # do custom stuff
        if commit:
            template.save()
        return template

    class Meta:
        model = EmailTemplate
        fields = ['sender', 'sender_name', 'name', 'subject', 'html_content']
        widgets = {'name': HiddenInput()}
