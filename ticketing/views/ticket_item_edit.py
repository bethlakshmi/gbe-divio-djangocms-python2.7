from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from ticketing.models import (
    TicketingEvents,
    TicketItem,
)
from ticketing.forms import TicketItemForm
from gbe.functions import validate_perms
from ticketing.views.functions import (
    delete_ticket_item,
    make_open_panel,
)
from gbe.models import UserMessage
from gbetext import (
    edit_ticket_message,
    intro_make_ticket_message,
)
from django.contrib import messages
import ast


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
            updated_tickets = ast.literal_eval(request.GET.get(
                'updated_tickets',
                '[]'))
            updated_tickets += [item.id]
            updated_events = ast.literal_eval(request.GET.get(
                'updated_events',
                '[]'))
            if 'submit_another' in request.POST:
                return HttpResponseRedirect(
                    ("%s?event_id=%s&updated_tickets=%s" +
                     "&updated_events=%s") % (
                        reverse('ticket_item_edit', urlconf='ticketing.urls'),
                        item.ticketing_event.event_id,
                        str(updated_tickets),
                        str(updated_events)))
            return HttpResponseRedirect(
                ('%s?conference=%s&open_panel=%s&updated_tickets=%s' +
                 '&updated_events=%s') % (
                    reverse(
                        'ticket_items',
                        urlconf='ticketing.urls'),
                    str(item.ticketing_event.conference.conference_slug),
                    make_open_panel(item.ticketing_event),
                    str(updated_tickets),
                    str(updated_events)))
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
