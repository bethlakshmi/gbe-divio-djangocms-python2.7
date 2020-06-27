#
# views.py - Contains Django Views for Ticketing
# edited by mdb 8/18/2014
# updated by BB 7/26/2015
#

from gbe_logging import logger
from django.shortcuts import render, get_object_or_404, render_to_response
from django.views.decorators.cache import never_cache
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.sites.shortcuts import get_current_site
from ticketing.models import (
    BrownPaperEvents,
    Purchaser,
    TicketItem,
    Transaction,
)
from ticketing.forms import *
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    validate_perms,
)
from gbe.models import (
    Conference,
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
    intro_ticket_message,
)
import pytz
from django.db.models import Q
from gbe.ticketing_idd_interface import get_ticket_form
from django.contrib import messages


def index(request):
    '''
    Represents the view for the main screen.  This will eventually be the
    equivalent of cost.php from the old site.
    '''

    events = BrownPaperEvents.objects.exclude(
        Q(conference__status='completed') | Q(
            act_submission_event=True) | Q(
            vendor_submission_event=True)).order_by(
        'conference__conference_slug')

    context = {'events': events,
               'user_id': request.user.id,
               'site_name': get_current_site(request).name
               }
    return render(request, 'ticketing/purchase_tickets.tmpl', context)


@never_cache
def ticket_items(request, conference_choice=None):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    validate_perms(request, ('Ticketing - Admin', ))

    if 'Import' in request.POST:
        import_ticket_items()

    conference_choice = request.GET.get('conference', None)
    open_panel = request.GET.get('open_panel', "")

    if conference_choice:
        events = BrownPaperEvents.objects.filter(
            conference__conference_slug=conference_choice)
    else:
        events = BrownPaperEvents.objects.exclude(
            conference__status='completed')
    intro = UserMessage.objects.get_or_create(
                view="ViewTicketItems",
                code="INTRO_MESSAGE",
                defaults={
                    'summary': "Introduction Message",
                    'description': intro_ticket_message})
    context = {'intro': intro[0].description,
               'act_pay_form': get_ticket_form("Act",
                                               get_current_conference()),
               'vendor_pay_form': get_ticket_form("Vendor",
                                                  get_current_conference()),
               'act_fees': events.filter(act_submission_event=True),
               'vendor_fees': events.filter(vendor_submission_event=True),
               'open_panel': open_panel,
               'events': events.filter(act_submission_event=False,
                                       vendor_submission_event=False),
               'conference_slugs': conference_slugs(),
               'conf_slug': conference_choice}
    return render(request, r'ticketing/ticket_items.tmpl', context)


@never_cache
def transactions(request):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    validate_perms(request, ('Ticketing - Transactions', ))

    count = -1
    error = ''

    if ('Sync' in request.POST):
        count = process_bpt_order_list()

    transactions = Transaction.objects.all()
    purchasers = Purchaser.objects.all()
    sync_time = get_bpt_last_poll_time()

    context = {'transactions': transactions,
               'purchasers': purchasers,
               'sync_time': sync_time,
               'error': error,
               'count': count}
    return render(request, r'ticketing/transactions.tmpl', context)


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
    another_button_text = "Edit & Add More"
    cancel_url = reverse('ticket_items', urlconf='ticketing.urls')
    can_delete = True
    button_text = 'Edit Ticket'
    if 'delete_item' in request.POST or 'delete_item' in request.GET:
        item = get_object_or_404(TicketItem, id=item_id)
        cancel_url = "%s?conference=%s&open_panel=%s" % (
            cancel_url,
            str(item.bpt_event.conference.conference_slug),
            make_open_panel(item.bpt_event))
        success = delete_ticket_item(request, "EditTicketItem", item)
        if success or 'delete_item' in request.GET:
            return HttpResponseRedirect(
                '%s?conference=%s&open_panel=%s' % (
                    reverse(
                        'ticket_items',
                        urlconf='ticketing.urls'),
                    str(item.bpt_event.conference.conference_slug),
                    make_open_panel(item.bpt_event)))
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
            if 'submit_another' in request.POST:
                return HttpResponseRedirect("%s?bpt_event_id=%s" % (
                    reverse('ticket_item_edit', urlconf='ticketing.urls'),
                    item.bpt_event.bpt_event_id))
            return HttpResponseRedirect(
                '%s?conference=%s&open_panel=%s' % (
                    reverse(
                        'ticket_items',
                        urlconf='ticketing.urls'),
                    str(item.bpt_event.conference.conference_slug),
                    make_open_panel(item.bpt_event)))
    else:
        if (item_id is not None):
            item = get_object_or_404(TicketItem, id=item_id)
            form = TicketItemForm(instance=item)
            cancel_url = "%s?conference=%s&open_panel=%s" % (
                cancel_url,
                str(item.bpt_event.conference.conference_slug),
                make_open_panel(item.bpt_event))
        else:
            title = "Create Ticket Item"
            button_text = 'Create Ticket'
            another_button_text = "Create & Add More"
            initial = None
            can_delete = False
            if request.GET and request.GET.get('bpt_event_id'):
                bpt_event = get_object_or_404(
                    BrownPaperEvents,
                    bpt_event_id=request.GET.get('bpt_event_id'))
                initial = {'bpt_event': bpt_event}
                cancel_url = "%s?open_panel=%s" % (cancel_url,
                                                   make_open_panel(bpt_event))
            form = TicketItemForm(initial=initial)

    context = {'forms': [form],
               'title': title,
               'intro': intro[0].description,
               'is_ticket': True,
               'button_text': button_text,
               'cancel_url': cancel_url,
               'can_delete': can_delete,
               'another_button_text': another_button_text,
              }
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)


def make_open_panel(bpt_event):
    open_panel = "ticket"
    if bpt_event.act_submission_event:
        open_panel = "act"
    elif bpt_event.vendor_submission_event:
        open_panel = "vendor"
    return open_panel

@never_cache
def bptevent_edit(request, event_id=None):
    '''
    Used to display a form for editing events.
    Deleting and adding events should only be done by an Admin
    '''
    validate_perms(request, ('Ticketing - Admin', ))
    event = None
    title = "Create Ticketed Event"
    button_text = 'Create Event'
    another_button_text = "Create & Add Tickets"
    intro = UserMessage.objects.get_or_create(
                view="EditBPTEvent",
                code="INTRO_MESSAGE",
                defaults={
                    'summary': "Introduction Message",
                    'description': intro_bptevent_message})
    cancel_url = reverse('ticket_items', urlconf='ticketing.urls')
    can_delete = True

    if event_id:
        event = get_object_or_404(BrownPaperEvents, id=event_id)
        title = "Edit Ticketed Event"
        button_text = 'Edit Event'
        another_button_text = "Edit & Add Tickets"
        cancel_url = "%s?open_panel=%s" % (cancel_url,
                                          make_open_panel(event))

    if event and ('delete_item' in request.POST or 'delete_item' in request.GET):
        success = True
        for ticket_item in event.ticketitems.all():
            item_deleted = delete_ticket_item(request,
                                              "EditBPTEvent",
                                              ticket_item)
            success = success and item_deleted
        if success:
            success_msg = UserMessage.objects.get_or_create(
                view="EditBPTEvent",
                code="DELETE_EVENT_SUCCESS",
                defaults={
                    'summary': "BPT Event Deleted",
                    'description': delete_event_success_message})
            messages.success(
                request,
                "%s  BPT Event Id: %s, Title: %s" % (
                    success_msg[0].description,
                    event.bpt_event_id,
                    event.title))
            event.delete()
        else:
            error = UserMessage.objects.get_or_create(
                view="EditBPTEvent",
                code="DELETE_EVENT_FAIL",
                defaults={
                    'summary': "Transactions Block Deletion",
                    'description': delete_event_fail_message})
            messages.error(
                request,
                "%s  BPT Event Id: %s, Title: %s" % (
                    error[0].description,
                    event.bpt_event_id,
                    event.title))
            form = BPTEventForm(instance=event)
        # go to ticket list if successful post, or if user started there
        if success or 'delete_item' in request.GET:
            return HttpResponseRedirect("%s?conference=%s&open_panel=%s" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(event.conference.conference_slug),
                make_open_panel(event)))

    elif (request.method == 'POST'):
        # save the item using the Forms API
        form = BPTEventForm(request.POST, instance=event)

        if form.is_valid():
            updated_event = form.save()
            success_msg = UserMessage.objects.get_or_create(
                view="EditBPTEvent",
                code="EDIT_EVENT_MESSAGE",
                defaults={
                    'summary': "BPT Event Edited Message",
                    'description': edit_event_message})
            messages.success(request, "%s  BPT Event Id: %s, Title: %s" % (
                success_msg[0].description,
                updated_event.bpt_event_id,
                updated_event.title))
            if 'submit_another' in request.POST:
                return HttpResponseRedirect("%s?bpt_event_id=%s" % (
                    reverse('ticket_item_edit', urlconf='ticketing.urls'),
                    updated_event.bpt_event_id))
            else:
                return HttpResponseRedirect(
                    "%s?conference=%s&open_panel=%s" % (
                        reverse('ticket_items', urlconf='ticketing.urls'),
                        str(updated_event.conference.conference_slug),
                        make_open_panel(updated_event)))
    else:
        form = BPTEventForm(instance=event)
        can_delete = False

    context = {'forms': [form],
               'intro': intro[0].description,
               'title': title,
               'is_ticket': False,
               'can_delete': can_delete,
               'cancel_url': cancel_url,
               'button_text': button_text,
               'another_button_text': another_button_text,
               }
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)
