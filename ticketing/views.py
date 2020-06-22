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
    intro_bptevent_message,
    intro_make_ticket_message,
    intro_ticket_message,
)
import pytz
from django.db.models import Q
from gbe.ticketing_idd_interface import get_ticket_form


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
    error = ''
    title = "Edit Ticket Item"

    if (request.method == 'POST'):

        if 'delete_item' in request.POST:

            item = get_object_or_404(TicketItem, id=item_id)

            # Check to see if ticket item is used in a
            # transaction before deleting.

            trans_exists = False
            for trans in Transaction.objects.all():
                if (trans.ticket_item.ticket_id == item.ticket_id):
                    trans_exists = True
                    break

            if (not trans_exists):
                item.delete()
                return HttpResponseRedirect(
                    '%s?conference=%s' % (
                        reverse(
                            'ticket_items',
                            urlconf='ticketing.urls'),
                        str(item.bpt_event.conference.conference_slug)))
            else:
                error = 'Cannot remove Ticket Item: %s \
                        It is used in a Transaction.' % item.ticket_id
                logger.error(error)
                form = TicketItemForm(instance=item)

        else:
            # save the item using the Forms API

            form = TicketItemForm(request.POST)
            if form.is_valid():
                item = form.save(str(request.user))
                form.save_m2m()
                return HttpResponseRedirect(
                    '%s?conference=%s' % (
                        reverse(
                            'ticket_items',
                            urlconf='ticketing.urls'),
                        str(item.bpt_event.conference.conference_slug)))
    else:
        if (item_id is not None):
            item = get_object_or_404(TicketItem, id=item_id)
            form = TicketItemForm(instance=item)
        else:
            title = "Create Ticket Item"
            initial = None
            if request.GET and request.GET.get('bpt_event_id'):
                initial = {'bpt_event': get_object_or_404(
                    BrownPaperEvents,
                    bpt_event_id=request.GET.get('bpt_event_id'))}
            form = TicketItemForm(initial=initial)

    context = {'forms': [form],
               'title': title,
               'intro': intro[0].description,
               'is_ticket': False,
               'error': error, 'can_delete': True}
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)


@never_cache
def bptevent_edit(request, event_id=None):
    '''
    Used to display a form for editing events.
    Deleting and adding events should only be done by an Admin
    '''
    validate_perms(request, ('Ticketing - Admin', ))
    event = None
    title = "Create Ticketed Event"
    intro = UserMessage.objects.get_or_create(
                view="EditBPTEvent",
                code="INTRO_MESSAGE",
                defaults={
                    'summary': "Introduction Message",
                    'description': intro_bptevent_message})

    if event_id:
        event = get_object_or_404(BrownPaperEvents, id=event_id)
        title = "Edit Ticketed Event"

    if (request.method == 'POST'):

        # save the item using the Forms API
        form = BPTEventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ticket_items',
                                                urlconf='ticketing.urls'))
    else:
        form = BPTEventForm(instance=event)

    context = {'forms': [form],
               'can_delete': False,
               'intro': intro[0].description,
               'title': title,
               'is_ticket': False}
    return render(request, r'ticketing/ticket_item_edit.tmpl', context)
