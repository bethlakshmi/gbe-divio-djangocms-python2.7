from django.forms import (
    Form,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import role_options
from gbe.email.forms import MultiConferenceField
from gbe.models import Conference


class SelectRoleForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    conference = MultiConferenceField(
        queryset=Conference.objects.all().order_by('conference_slug'),
        widget=CheckboxSelectMultiple(),
        required=True,)
    roles = MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple(),
        choices=role_options)


class SecretRoleInfoForm(SelectRoleForm):
    conference = ModelMultipleChoiceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        widget=MultipleHiddenInput(),
        required=True)
    roles = MultipleChoiceField(
        widget=MultipleHiddenInput(),
        required=True,
        choices=role_options)
