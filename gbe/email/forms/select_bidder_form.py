from django.forms import (
    Form,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import acceptance_states
from gbe_forms_text import inform_about_options
from gbe.models import Conference


class MultiConferenceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.conference_slug


class SelectBidderForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    conference = MultiConferenceField(
        queryset=Conference.objects.all().order_by('conference_slug'),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,)
    bid_type = MultipleChoiceField(
        required=True,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True)
    profile_interest = MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        choices=inform_about_options)
    x_conference = MultiConferenceField(
        queryset=Conference.objects.all().order_by('conference_slug'),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Conference",
        required=False)
    x_bid_type = MultipleChoiceField(
        label="Bid type",
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False)
    x_state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="State",
        required=False)
    x_profile_interest = MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Profile Interest",
        choices=inform_about_options)

    def __init__(self, *args, **kwargs):
        if 'bid_types' in kwargs:
            bid_types = kwargs.pop('bid_types')
        super(SelectBidderForm, self).__init__(*args, **kwargs)
        self.fields['bid_type'].choices = bid_types
        self.fields['x_bid_type'].choices = bid_types


class SecretBidderInfoForm(SelectBidderForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget = MultipleHiddenInput()

