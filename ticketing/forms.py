#
# forms.py - Contains Django Forms for Ticketing based on forms.ModelForm
# edited by mdb 5/28/2014
# edited by bb 7/27/2015
#

from ticketing.models import (
    TicketingEvents,
    TicketItem,
)
from gbe.functions import get_ticketable_gbe_events
from django import forms
from gbe.models import Conference
from gbe_forms_text import (
    ticketing_event_help_text,
    ticketing_event_labels,
    donation_help_text,
    donation_labels,
    link_event_help_text,
    link_event_labels,
    ticket_item_labels,
    ticket_item_help_text,
)
from django.forms.widgets import CheckboxSelectMultiple
from tempus_dominus.widgets import DatePicker


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


class PickBPTEventField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s - %s" % (obj.event_id, obj.title)


class LinkBPTEventForm(forms.ModelForm):
    '''
    Used in event creation in gbe to set up ticket info when making a new class
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    ticketing_events = PickBPTEventField(
        queryset=TicketingEvents.objects.exclude(
            conference__status="completed").order_by('event_id'),
        required=False,
        label=link_event_labels['ticketing_events'],
        widget=CheckboxSelectMultiple(),)
    event_id = forms.IntegerField(
        required=False,
        label=link_event_labels['event_id'])
    display_icon = forms.CharField(
        required=False,
        label=link_event_labels['display_icon'],
        help_text=link_event_help_text['display_icon'])

    class Meta:
        model = TicketingEvents
        fields = ['event_id', 'display_icon']
        labels = link_event_labels
        help_texts = link_event_help_text

    def __init__(self, *args, **kwargs):
        super(LinkBPTEventForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            self.fields[
                'ticketing_events'].queryset = TicketingEvents.objects.filter(
                conference=initial['conference']).order_by('event_id')


class BPTEventForm(forms.ModelForm):
    '''
    Used to create a form for editing the whole event.  Used by the
    TicketItemEdit view.
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    linked_events = forms.ModelMultipleChoiceField(
        queryset=get_ticketable_gbe_events().order_by('e_title'),
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
            'source',
            'title',
            'description',
            'display_icon',
            'act_submission_event',
            'vendor_submission_event',
            'linked_events',
            'include_conference',
            'include_most',
            'badgeable',
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
