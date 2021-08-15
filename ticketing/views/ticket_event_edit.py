from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from ticketing.models import TicketingEvents
from ticketing.forms import BPTEventForm
from gbe.functions import validate_perms
from gbe.models import UserMessage
from gbetext import (
    edit_event_message,
    delete_event_success_message,
    delete_event_fail_message,
    intro_bptevent_message,
)
from django.contrib import messages
from ticketing.views.functions import (
    delete_ticket_item,
    make_open_panel,
)


@never_cache
def ticket_event_edit(request, event_id=None):
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
        event = get_object_or_404(TicketingEvents, id=event_id)
        title = "Edit Ticketed Event"
        button_text = 'Save'
        another_button_text = "Save & Add Tickets"
        cancel_url = "%s?open_panel=%s" % (cancel_url,
                                           make_open_panel(event))

    if event and (
            'delete_item' in request.POST or 'delete_item' in request.GET):
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
                    event.event_id,
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
                    event.event_id,
                    event.title))
            form = BPTEventForm(instance=event)
        # go to ticket list if successful post, or if user started there
        if success or 'delete_item' in request.GET:
            return HttpResponseRedirect(
                "%s?conference=%s&open_panel=%s&updated_events=%s" % (
                    reverse('ticket_items', urlconf='ticketing.urls'),
                    str(event.conference.conference_slug),
                    make_open_panel(event),
                    str([event.id])))

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
                updated_event.event_id,
                updated_event.title))
            if 'submit_another' in request.POST:
                return HttpResponseRedirect(
                    "%s?event_id=%s&updated_events=%s" % (
                        reverse('ticket_item_edit', urlconf='ticketing.urls'),
                        updated_event.event_id,
                        str([updated_event.id])))
            else:
                return HttpResponseRedirect(
                    "%s?conference=%s&open_panel=%s&updated_events=%s" % (
                        reverse('ticket_items', urlconf='ticketing.urls'),
                        str(updated_event.conference.conference_slug),
                        make_open_panel(updated_event),
                        str([updated_event.id])))
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
