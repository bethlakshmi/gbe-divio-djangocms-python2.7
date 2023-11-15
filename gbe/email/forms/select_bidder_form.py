from django.forms import (
    Form,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.core.exceptions import ValidationError
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import acceptance_states
from gbe_forms_text import (
    bidder_select_one,
    bid_conf_required,
    bid_state_required,
    bid_type_required,
    bid_conf_exclude,
    bid_state_exclude,
    bid_type_exclude,
    inform_about_options,
)
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
        required=False,)
    bid_type = MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}))
    state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False)
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

    def clean(self):
        from gbe.models import UserMessage as UMsg
        cleaned_data = super(SelectBidderForm, self).clean()

        # temp variables for reuseable readability
        con_len = len(cleaned_data['conference'])
        bid_len = len(cleaned_data['bid_type'])
        state_len = len(cleaned_data['state'])
        interest_len = len(cleaned_data['profile_interest'])
        x_con_len = len(cleaned_data['x_conference'])
        x_bid_len = len(cleaned_data['x_bid_type'])
        x_state_len = len(cleaned_data['x_state'])

        if con_len == 0 and bid_len == 0 and state_len== 0 and (
                interest_len == 0):
            raise ValidationError(
                UMsg.objects.get_or_create(
                    view="MailToBiddersView",
                    code="SELECT_BID_OR_INTEREST",
                    defaults={
                        'summary': "User did not select any criteria",
                        'description': bidder_select_one,
                        })[0].description,
                code='Invalid')
        else:
            if (con_len + bid_len + state_len) > 0 and con_len == 0:
                self._errors['conference'] = UMsg.objects.get_or_create(
                    view="MailToBiddersView",
                    code="CONFERENCE_REQUIRED_FOR_BID",
                    defaults={
                        'summary': "Conference required",
                        'description': bid_conf_required
                        })[0].description
            if (con_len + bid_len + state_len) > 0 and bid_len == 0:
                self._errors['bid_type'] = UMsg.objects.get_or_create(
                    view="MailToBiddersView",
                    code="TYPE_REQUIRED_FOR_BID",
                    defaults={
                        'summary': "Bid Type required",
                        'description': bid_type_required
                        })[0].description
            if (con_len + bid_len + state_len) > 0 and state_len == 0:
                self._errors['state'] = UMsg.objects.get_or_create(
                    view="MailToBiddersView",
                    code="STATE_REQUIRED_FOR_BID",
                    defaults={
                        'summary': "Bid State required",
                        'description': bid_state_required
                        })[0].description

        if (x_con_len + x_bid_len + x_state_len) > 0 and x_con_len == 0:
            self._errors['x_conference'] = UMsg.objects.get_or_create(
                view="MailToBiddersView",
                code="CONFERENCE_REQUIRED_FOR_EXCLUDE_BID",
                defaults={
                    'summary': "Conference required - Exclude",
                    'description': bid_conf_exclude
                    })[0].description
        if (x_con_len + x_bid_len + x_state_len) > 0 and x_bid_len == 0:
            self._errors['x_bid_type'] = UMsg.objects.get_or_create(
                view="MailToBiddersView",
                code="TYPE_REQUIRED_FOR_EXCLUDE_BID",
                defaults={
                    'summary': "Bid Type required - Exclude",
                    'description': bid_type_exclude
                    })[0].description
        if (x_con_len + x_bid_len + x_state_len) > 0 and x_state_len == 0:
            self._errors['x_state'] = UMsg.objects.get_or_create(
                view="MailToBiddersView",
                code="STATE_REQUIRED_FOR_EXCLUDE_BID",
                defaults={
                    'summary': "Bid State required - Exclude",
                    'description': bid_state_exclude
                    })[0].description
        return self.cleaned_data

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

