from ticketing.models import (
    BrownPaperEvents,
    TicketItem,
)
from itertools import chain
from datetime import datetime


def get_tickets(linked_event, most=False, conference=False):
    general_events = []

    if most:
        general_events = BrownPaperEvents.objects.filter(
            include_most=True,
            conference=linked_event.e_conference)
    if conference:
        general_events = list(chain(
            general_events,
            BrownPaperEvents.objects.filter(
                include_conference=True,
                conference=linked_event.e_conference)))

    general_events = list(chain(
        general_events,
        BrownPaperEvents.objects.filter(
            linked_events=linked_event)))

    ticket_events = []

    for event in general_events:
        if event.live_ticket_count > 0 and event not in ticket_events:
            ticket_events += [event]
    return ticket_events


def get_fee_list(bid_type, conference):
    ticket_items = []
    ticket_items = TicketItem.objects.filter(
        bpt_event__conference=conference, live=True, has_coupon=False).exclude(
        start_time__lt=datetime.now(), end_time__gt=datetime.now())
    if bid_type == "Vendor":
        ticket_items = ticket_items.filter(
            bpt_event__vendor_submission_event=True)
    elif bid_type == "Act":
        ticket_items = ticket_items.filter(
            bpt_event__act_submission_event=True)
    return ticket_items
