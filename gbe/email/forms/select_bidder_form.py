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
from django.core.exceptions import ValidationError


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

    def __init__(self, *args, **kwargs):
        if 'bid_types' in kwargs:
            bid_types = kwargs.pop('bid_types')
        super(SelectBidderForm, self).__init__(*args, **kwargs)
        self.fields['bid_type'].choices = bid_types
        self.fields['x_bid_type'].choices = bid_types

    def clean(self):
        # run the parent validation first
        cleaned_data = super(SelectBidderForm, self).clean()

        # if any exclusion is set, they all must be
        if not (self.cleaned_data['x_conference'] and
                self.cleaned_data['x_bid_type'] and
                self.cleaned_data['x_bid_type']) and (
                self.cleaned_data['x_conference'] or
                self.cleaned_data['x_bid_type'] or
                self.cleaned_data['x_bid_type']):
            raise ValidationError(
                'To use exclusions, please include all 3 choices')
        return cleaned_data


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
    x_conference = ModelMultipleChoiceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        widget=MultipleHiddenInput(),
        required=False)
    x_bid_type = MultipleChoiceField(
        widget=MultipleHiddenInput(),
        required=False)
    x_state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=MultipleHiddenInput(),
        required=False)
