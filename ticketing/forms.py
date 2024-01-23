#
# forms.py - Contains Django Forms for Ticketing based on forms.ModelForm
# edited by mdb 5/28/2014
# edited by bb 7/27/2015
#

from ticketing.models import (
    TicketingEvents,
    TicketItem,
    TicketType,
    TicketPackage,
    Transaction,
)
from gbe.functions import get_ticketable_gbe_events
from django import forms
from gbe.models import (
    Conference,
    Profile,
)
from gbe_forms_text import (
    ticketing_event_help_text,
    ticketing_event_labels,
    donation_help_text,
    donation_labels,
    link_event_labels,
    ticket_item_labels,
    ticket_item_help_text,
)
from django.forms.widgets import CheckboxSelectMultiple
from tempus_dominus.widgets import DatePicker
from dal import autocomplete
from django.db.models import Q
from django.urls import reverse_lazy


class TicketItemForm(forms.ModelForm):
    '''
    Used to create a form for editing ticket item.  Used by the TicketItemEdit
    view.
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    ticketing_event = forms.ModelChoiceField(
        queryset=TicketingEvents.objects.exclude(
            conference__status='completed'),
        empty_label=None,
        label=ticket_item_labels['ticketing_event'])
    start_time = forms.DateField(
        help_text=ticket_item_help_text['start_time'],
        required=False,
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True},
            options={
                'format': "M/D/YYYY"}))
    end_time = forms.DateField(
        help_text=ticket_item_help_text['end_time'],
        required=False,
        widget=DatePicker(
            attrs={
                'append': 'fa fa-calendar',
                'icon_toggle': True},
            options={
                'format': "M/D/YYYY"}))

    class Meta:
        model = TicketItem
        fields = ['ticket_id',
                  'title',
                  'cost',
                  'ticketing_event',
                  'has_coupon',
                  'special_comp',
                  'live',
                  'start_time',
                  'end_time',
                  'is_minimum',
                  'add_on'
                  ]
        labels = ticket_item_labels
        help_texts = ticket_item_help_text

    def save(self, user, commit=True):
        form = super(TicketItemForm, self).save(commit=False)
        form.modified_by = user

        exists = TicketItem.objects.filter(ticket_id=form.ticket_id)
        if (exists.count() > 0):
            form.id = exists[0].id

        if commit:
            form.save()
        return form


class TicketTypeForm(TicketItemForm):
    linked_events = forms.ModelMultipleChoiceField(
        queryset=get_ticketable_gbe_events().order_by('title'),
        required=False,
        label=ticketing_event_labels['linked_events'])

    class Meta:
        model = TicketType
        fields = ['ticket_id',
                  'title',
                  'cost',
                  'ticketing_event',
                  'has_coupon',
                  'special_comp',
                  'live',
                  'start_time',
                  'end_time',
                  'is_minimum',
                  'conference_only_pass',
                  'linked_events'
                  ]
        labels = ticket_item_labels
        help_texts = ticket_item_help_text

    def save(self, user, commit=True):
        # broken out separate, and skips TicketItemForm save because
        # the Ticket Item Form was breaking the natural m2m save
        form = super(TicketItemForm, self).save(commit=commit)
        form.modified_by = user

        if commit:
            form.save()
        return form


class TicketPackageForm(TicketItemForm):

    class Meta:
        model = TicketPackage
        fields = ['ticket_id',
                  'title',
                  'cost',
                  'ticketing_event',
                  'has_coupon',
                  'special_comp',
                  'live',
                  'start_time',
                  'end_time',
                  'is_minimum',
                  'ticket_types',
                  'conference_only_pass',
                  'whole_shebang',
                  ]
        labels = ticket_item_labels
        help_texts = ticket_item_help_text


class PickBPTEventField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s - %s" % (obj.event_id, obj.title)


class LinkTicketsForm(forms.Form):
    '''
    Used in event creation in gbe to set up ticket info when making a new class
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    ticketing_events = PickBPTEventField(
        queryset=TicketingEvents.objects.exclude(
            conference__status="completed",
            source=3).order_by('title'),
        required=False,
        label=link_event_labels['ticketing_events'],
        widget=CheckboxSelectMultiple(),)
    ticket_types = forms.ModelMultipleChoiceField(
        queryset=TicketType.objects.filter(ticketing_event__source=3).exclude(
            ticketing_event__conference__status="completed").order_by('title'),
        required=False,
        label=link_event_labels['ticket_types'],
        widget=CheckboxSelectMultiple())

    class Meta:
        model = TicketingEvents
        labels = link_event_labels

    def __init__(self, *args, **kwargs):
        super(LinkTicketsForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            self.fields[
                'ticketing_events'].queryset = TicketingEvents.objects.filter(
                conference=initial['conference']).exclude(source=3).order_by(
                'title')
            self.fields['ticket_types'].queryset = TicketType.objects.filter(
                ticketing_event__conference=initial['conference']
                ).order_by('title')


class BPTEventForm(forms.ModelForm):
    '''
    Used to create a form for editing the whole event.  Used by the
    TicketItemEdit view.
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    linked_events = forms.ModelMultipleChoiceField(
        queryset=get_ticketable_gbe_events().order_by('title'),
        required=False,
        label=ticketing_event_labels['linked_events'])
    conference = forms.ModelChoiceField(
        queryset=Conference.objects.exclude(
            status='completed'),
        empty_label=None)

    class Meta:
        model = TicketingEvents
        fields = [
            'conference',
            'event_id',
            'slug',
            'source',
            'title',
            'description',
            'display_icon',
            'act_submission_event',
            'vendor_submission_event',
            'linked_events',
            'include_conference',
            'include_most',
            'ticket_style']
        labels = ticketing_event_labels
        help_texts = ticketing_event_help_text


class PickTicketField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s - $%s (USD)" % (obj.title, obj.cost)


class PickTicketsField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s - $%s (USD)" % (obj.title, obj.cost)


class DonationForm(forms.Form):
    donation = forms.DecimalField(required=True,
                                  label=donation_labels['donation'],
                                  help_text=donation_help_text['donation'])

    def __init__(self, *args, **kwargs):
        super(DonationForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs.get('initial', {})
            self.fields['donation'] = forms.DecimalField(
                required=True,
                label=donation_labels['donation'],
                help_text=donation_help_text['donation'],
                min_value=initial.get('donation_min', 0),
                initial=initial.get('donation', 0))


class TicketPayForm(forms.Form):
    main_ticket = PickTicketField(
        queryset=TicketItem.objects.all(),
        required=True,
        empty_label=None)
    add_ons = PickTicketsField(
        queryset=TicketItem.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple)


class CompFeeForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    ticket_item = forms.ModelChoiceField(
        queryset=TicketItem.objects.exclude(
            ticketing_event__conference__status='completed',).filter(
            Q(ticketing_event__act_submission_event=True) |
            Q(ticketing_event__vendor_submission_event=True),
            special_comp=True).order_by(
            'ticketing_event',
            'title'))
    profile = forms.ModelChoiceField(
        queryset=Profile.objects.filter(user_object__is_active=True),
        widget=autocomplete.ModelSelect2(
            url=reverse_lazy('profile-autocomplete', urlconf='gbe.urls')))

    class Meta:
        model = Transaction
        fields = ['ticket_item', ]
