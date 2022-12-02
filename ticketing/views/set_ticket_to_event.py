from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.urls import reverse
from ticketing.models import TicketingEvents
from gbe.functions import validate_perms
from ticketing.views.functions import make_open_panel
from gbe.models import UserMessage
from gbetext import (
    link_event_to_ticket_success_msg,
    unlink_event_to_ticket_success_msg,
)
from django.contrib import messages
from scheduler.idd import get_occurrence


@never_cache
def set_ticket_to_event(request, event_id, state, gbe_event_id):
    validate_perms(request, ('Ticketing - Admin', ))
    ticketing_event = get_object_or_404(TicketingEvents, event_id=event_id)
    response = get_occurrence(gbe_event_id)
    if response.errors and response.errors[0].code == "OCCURRENCE_NOT_FOUND":
        raise Http404

    gbe_event = response.occurrence
    if state == "on" and not ticketing_event.linked_events.filter(
            id=gbe_event_id).exists():
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
                gbe_event.title))
    elif state == "off" and ticketing_event.linked_events.filter(
            id=gbe_event_id).exists():
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
                gbe_event.title))
    return HttpResponseRedirect(
        '%s?conference=%s&open_panel=%s&updated_events=%s' % (
            reverse('ticket_items', urlconf='ticketing.urls'),
            ticketing_event.conference.conference_slug,
            make_open_panel(ticketing_event),
            str([ticketing_event.id])))
