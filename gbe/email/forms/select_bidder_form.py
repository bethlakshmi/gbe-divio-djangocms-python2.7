from django.forms import (
    Form,
    HiddenInput,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import acceptance_states
from gbe.models import Conference


class MultiConferenceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.conference_slug


class SelectBidderForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    conference = MultiConferenceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,)
    bid_type = MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True)


class SecretBidderInfoForm(SelectBidderForm):
    conference = ModelMultipleChoiceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        widget=MultipleHiddenInput(),
        required=True)
    bid_type = MultipleChoiceField(
        widget=MultipleHiddenInput(),
        required=True)
    state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=MultipleHiddenInput(),
        required=True)
