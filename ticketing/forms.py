#
# forms.py - Contains Django Forms for Ticketing based on forms.ModelForm
# edited by mdb 5/28/2014
# edited by bb 7/27/2015
#

from ticketing.models import *
from django import forms
from gbe.models import Show, GenericEvent, Event
from gbe_forms_text import *
from django.db.models import Q
from django.forms.widgets import CheckboxSelectMultiple


class TicketItemForm(forms.ModelForm):
    '''
    Used to create a form for editing ticket item.  Used by the TicketItemEdit
    view.
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    bpt_event = forms.ModelChoiceField(
                            queryset=BrownPaperEvents.objects.all(),
                            empty_label=None)

    class Meta:
        model = TicketItem
        fields = ['ticket_id',
                  'title',
                  'cost',
                  'bpt_event',
                  'has_coupon',
                  'live',
                  ]
        labels = ticket_item_labels

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
        return "%s - %s" % (obj.bpt_event_id, obj.title)


class LinkBPTEventForm(forms.ModelForm):
    '''
    Used in event creation in gbe to set up ticket info when making a new class
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    bpt_events = PickBPTEventField(
        queryset=BrownPaperEvents.objects.exclude(
            conference__status="completed").order_by('bpt_event_id'),
        required=False,
        label=link_event_labels['bpt_events'],
        widget=CheckboxSelectMultiple(),)
    bpt_event_id = forms.IntegerField(
        required=False,
        label=link_event_labels['bpt_event_id'])
    display_icon = forms.CharField(
        required=False,
        label=link_event_labels['display_icon'],
        help_text=link_event_help_text['display_icon'])

    class Meta:
        model = BrownPaperEvents
        fields = [
            'bpt_event_id',
            'display_icon']
        labels = link_event_labels
        help_texts = link_event_help_text

    def __init__(self, *args, **kwargs):
        super(LinkBPTEventForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            self.fields[
                'bpt_events'].queryset = BrownPaperEvents.objects.filter(
                conference=initial['conference']).order_by('bpt_event_id')


class BPTEventForm(forms.ModelForm):
    '''
    Used to create a form for editing the whole event.  Used by the
    TicketItemEdit view.
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    shows = Show.objects.all()
    genericevents = GenericEvent.objects.exclude(type="Volunteer")
    event_set = Event.objects.filter(
        Q(show__in=shows) |
        Q(genericevent__in=genericevents)).exclude(
            e_conference__status="completed")
    linked_events = forms.ModelMultipleChoiceField(
        queryset=event_set,
        required=False,
        label=bpt_event_labels['linked_events'])

    class Meta:
        model = BrownPaperEvents
        fields = [
            'title',
            'description',
            'display_icon',
            'primary',
            'act_submission_event',
            'vendor_submission_event',
            'linked_events',
            'include_conference',
            'include_most',
            'badgeable',
            'ticket_style',
            'conference']
        labels = bpt_event_labels
        help_texts = bpt_event_help_text
