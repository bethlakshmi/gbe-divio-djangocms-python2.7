from django.forms import (
    CharField,
    HiddenInput,
    ModelForm,
    Textarea,
    TextInput,
)
from post_office.models import EmailTemplate
from tinymce.widgets import TinyMCE
from django.utils.html import strip_tags


class EmailTemplateForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    html_content = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}),
        label="Message")
    sender = CharField(max_length=100,
                       required=True,
                       label="From")
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
        fields = ['sender', 'name', 'subject', 'html_content']
        widgets = {'name': HiddenInput()}
