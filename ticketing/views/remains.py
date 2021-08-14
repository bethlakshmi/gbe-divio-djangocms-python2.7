#
# views.py - Contains Django Views for Ticketing
# edited by mdb 8/18/2014
# updated by BB 7/26/2015
#

from gbe_logging import logger
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from ticketing.models import (
    TicketingEvents,
    Purchaser,
    TicketItem,
    Transaction,
)
from ticketing.forms import *
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    get_ticketable_gbe_events,
    validate_perms,
)
from gbe.models import (
    Conference,
    Event,
    UserMessage,
)
from gbetext import (
    edit_event_message,
    edit_ticket_message,
    delete_event_success_message,
    delete_event_fail_message,
    delete_ticket_fail_message,
    delete_ticket_success_message,
    intro_bptevent_message,
    intro_make_ticket_message,
    intro_ticket_assign_message,
    intro_ticket_message,
    link_event_to_ticket_success_msg,
    purchase_intro_msg,
    unlink_event_to_ticket_success_msg,
)
import pytz
from django.db.models import (
    Max,
    Min,
    Q,
)
from gbe.ticketing_idd_interface import get_ticket_form
from django.contrib import messages


def index(request):
    '''
    Represents the view for the main screen.  This will eventually be the
    equivalent of cost.php from the old site.
    '''
    ''' Query means - get upcoming/current conference BPT events, annotate
      with a max and min price but only for the public tickets (not comps,
      not discounts), then sort by conference and descending highest price.
      The first thing on the list should be the whole weekend ticket, for the
      soonest conference.'''
    events = TicketingEvents.objects.exclude(
        Q(conference__status='completed') | Q(
            act_submission_event=True) | Q(
            vendor_submission_event=True)).annotate(
            max_price=Max('ticketitems__cost',
                          filter=Q(ticketitems__live=True,
                                   ticketitems__has_coupon=False))).annotate(
            min_price=Min('ticketitems__cost',
                          filter=Q(ticketitems__live=True,
                                   ticketitems__has_coupon=False))).order_by(
        'conference__conference_slug', '-max_price', '-min_price')
    intro = UserMessage.objects.get_or_create(
            view="ListPublicTickets",
            code="INTRO_MESSAGE",
            defaults={
                'summary': "Intro at top of list",
                'description': purchase_intro_msg})
    context = {'events': events,
               'user_id': request.user.id,
               'site_name': get_current_site(request).name,
               'introduction': intro[0].description
               }
    return render(request, 'ticketing/purchase_tickets.tmpl', context)


@never_cache
def set_ticket_to_event(request, event_id, state, gbe_eventitem_id):
    validate_perms(request, ('Ticketing - Admin', ))
    ticketing_event = get_object_or_404(TicketingEvents, event_id=event_id)
    gbe_event = get_object_or_404(Event, eventitem_id=gbe_eventitem_id)
    if state == "on" and not ticketing_event.linked_events.filter(
            eventitem_id=gbe_eventitem_id).exists():
        ticketing_event.linked_events.add(gbe_event)
        ticketing_event.save()
        success_msg = UserMessage.objects.get_or_create(
            view="LinkEventToTicket",
            code="EVENT_LINKED_MESSAGE",
            defaults={
                'summary': "Ticket Was Linked to GBE Event",
                'description': link_event_to_ticket_success_msg})
        messages.success(
            request,
            "%s  Ticket Event Item: %s, GBE Event: %s" % (
                success_msg[0].description,
                ticketing_event.title,
                gbe_event.e_title))
    elif state == "off" and ticketing_event.linked_events.filter(
            eventitem_id=gbe_eventitem_id).exists():
        ticketing_event.linked_events.remove(gbe_event)
        success_msg = UserMessage.objects.get_or_create(
            view="LinkEventToTicket",
            code="EVENT_UNLINKED_MESSAGE",
            defaults={
                'summary': "Ticket Was Removed from GBE Event",
                'description': unlink_event_to_ticket_success_msg})
        messages.success(
            request,
            "%s  Ticket Event Item: %s, GBE Event: %s" % (
                success_msg[0].description,
                ticketing_event.title,
                gbe_event.e_title))
    return HttpResponseRedirect(
        '%s?conference=%s&open_panel=%s&updated_events=%s' % (
            reverse('ticket_items', urlconf='ticketing.urls'),
            ticketing_event.conference.conference_slug,
            make_open_panel(ticketing_event),
            str([ticketing_event.id])))


def delete_ticket_item(request, view, item):
    success = False
    if Transaction.objects.filter(ticket_item=item).exists():
        error = UserMessage.objects.get_or_create(
            view=view,
            code="DELETE_FAIL",
            defaults={
                'summary': "Transactions Block Deletion",
                'description': delete_ticket_fail_message})
        messages.error(
            request,
            "%s  Ticket Item Id: %s, Title: %s" % (
                error[0].description,
                item.ticket_id,
                item.title))
    else:
        success_msg = UserMessage.objects.get_or_create(
            view=view,
            code="DELETE_SUCCESS",
            defaults={
                'summary': "Ticket Item Deleted",
                'description': delete_ticket_success_message})
        messages.success(
            request,
            "%s  Ticket Item Id: %s, Title: %s" % (
                success_msg[0].description,
                item.ticket_id,
                item.title))
        item.delete()
        success = True
    return success


@never_cache
def ticket_item_edit(request, item_id=None):
    '''
    Used to display a form for editing ticket, adding or removing ticket items.
    '''
    validate_perms(request, ('Ticketing - Admin', ))
    intro = UserMessage.objects.get_or_create(
                view="EditTicketItem",
                code="INTRO_MESSAGE",
                defaults={
                    'summary': "Introduction Message",
                    'description': intro_make_ticket_message})
    title = "Edit Ticket Item"
    another_button_text = "Save & Add More"
    cancel_url = reverse('ticket_items', urlconf='ticketing.urls')
    can_delete = True
    button_text = 'Save'
    if 'delete_item' in request.POST or 'delete_item' in request.GET:
        item = get_object_or_404(TicketItem, id=item_id)
        cancel_url = "%s?conference=%s&open_panel=%s" % (
            cancel_url,
            str(item.ticketing_event.conference.conference_slug),
            make_open_panel(item.ticketing_event))
        success = delete_ticket_item(request, "EditTicketItem", item)
        if success or 'delete_item' in request.GET:
            return HttpResponseRedirect(
                '%s?conference=%s&open_panel=%s&updated_events=%s' % (
                    reverse(
                        'ticket_items',
                        urlconf='ticketing.urls'),
                    str(item.ticketing_event.conference.conference_slug),
                    make_open_panel(item.ticketing_event),
                    str([item.ticketing_event.id])))
        else:
            form = TicketItemForm(instance=item)

    elif (request.method == 'POST'):
        form = TicketItemForm(request.POST)
        if form.is_valid():
            item = form.save(str(request.user))
            form.save_m2m()
            success_msg = UserMessage.objects.get_or_create(
                view="EditTicketItem",
                code="EDIT_TICKET_MESSAGE",
                defaults={
                    'summary': "Ticket Edited Message",
                    'description': edit_ticket_message})
            messages.success(request, "%s  Ticket Item Id: %s, Title: %s" % (
                success_msg[0].description,
                item.ticket_id,
                item.title))
            updated_tickets = eval(request.GET.get('updated_tickets', '[]'))
            updated_tickets += [item.id]
            if 'submit_another' in request.POST:
                return HttpResponseRedirect(
                    ("%s?event_id=%s&updated_tickets=%s" +
                     "&updated_events=%s") % (
                        reverse('ticket_item_edit', urlconf='ticketing.urls'),
                        item.ticketing_event.event_id,
                        str(updated_tickets),
                        request.GET.get('updated_events', '[]')))
            return HttpResponseRedirect(
                ('%s?conference=%s&open_panel=%s&updated_tickets=%s' +
                 '&updated_events=%s') % (
                    reverse(
                        'ticket_items',
                        urlconf='ticketing.urls'),
                    str(item.ticketing_event.conference.conference_slug),
                    make_open_panel(item.ticketing_event),
                    str(updated_tickets),
                    request.GET.get('updated_events', '[]')))
    else:
        if (item_id is not None):
            item = get_object_or_404(TicketItem, id=item_id)
            form = TicketItemForm(instance=item)
            cancel_url = "%s?conference=%s&open_panel=%s" % (
                cancel_url,
                str(item.ticketing_event.conference.conference_slug),
                make_open_panel(item.ticketing_event))
        else:
            title = "Create Ticket Item"
            button_text = 'Create Ticket'
            another_button_text = "Create & Add More"
            initial = None
            can_delete = False
            if request.GET and request.GET.get('event_id'):
                ticketing_event = get_object_or_404(
                    TicketingEvents,
                    event_id=request.GET.get('event_id'))
                initial = {'ticketing_event': ticketing_event}
                cancel_url = "%s?open_panel=%s" % (
                    cancel_url,
                    make_open_panel(ticketing_event))
            form = TicketItemForm(initial=initial)

    context = {'forms': [form],
               'title': title,
               'intro': intro[0].description,
               'is_ticket': True,
               'button_text': button_text,
               'cancel_url': cancel_url,
               'can_delete': can_delete,
               'another_button_text': another_button_text}
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)


def make_open_panel(ticketing_event):
    open_panel = "ticket"
    if ticketing_event.act_submission_event:
        open_panel = "act"
    elif ticketing_event.vendor_submission_event:
        open_panel = "vendor"
    return open_panel
