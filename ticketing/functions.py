from itertools import chain
from datetime import datetime
from ticketing.models import (
    TicketingEvents,
    TicketItem,
)
from ticketing.eventbrite import import_eb_ticket_items
from ticketing.brown_paper import import_bpt_ticket_items


def import_ticket_items(event=None):
        # Since Eventbrite autosyncs events, we would only need to manually
        # import BPT
        msg = "0"
        is_success = True
        events = None
        if event is None:
            msg, is_success = import_eb_ticket_items()
            if not is_success:
                return msg, is_success
        else:
            events = [event]
        count = import_bpt_ticket_items(events)

        return "EventBrite: %s, BPT: imported %d tickets" % (
            msg,
            count), is_success


def get_tickets(linked_event, most=False, conference=False):
    general_events = []

    if most:
        general_events = TicketingEvents.objects.filter(
            include_most=True,
            conference=linked_event.e_conference)
    if conference:
        general_events = list(chain(
            general_events,
            TicketingEvents.objects.filter(
                include_conference=True,
                conference=linked_event.e_conference)))

    general_events = list(chain(
        general_events,
        TicketingEvents.objects.filter(
            linked_events=linked_event)))

    ticket_events = []

    for event in general_events:
        if event.live_ticket_count > 0 and event not in ticket_events:
            ticket_events += [event]
    return ticket_events


def get_fee_list(bid_type, conference):
    ticket_items = []
    ticket_items = TicketItem.objects.filter(
        ticketing_event__conference=conference,
        live=True,
        has_coupon=False).exclude(
        start_time__gt=datetime.now()).exclude(end_time__lt=datetime.now())
    if bid_type == "Vendor":
        ticket_items = ticket_items.filter(
            ticketing_event__vendor_submission_event=True)
    elif bid_type == "Act":
        ticket_items = ticket_items.filter(
            ticketing_event__act_submission_event=True)
    return ticket_items
