from itertools import chain
from datetime import datetime
from ticketing.models import (
    TicketingEvents,
    TicketItem,
)
from ticketing.eventbrite import import_eb_ticket_items
from ticketing.brown_paper import import_bpt_ticket_items
from gbetext import class_styles

def import_ticket_items():
        # Since Eventbrite autosyncs events, we would only need to manually
        # import BPT
        msg = "0"
        is_success = True
        msg, is_success = import_eb_ticket_items()
        count = import_bpt_ticket_items()

        return [(msg, is_success),
                ("BPT: imported %d tickets" % count, True)]


def get_tickets(linked_event):
    general_events = []
    if linked_event.event_style in ["Special", "Drop-In", "Show"]:
        general_events = TicketingEvents.objects.filter(
            include_most=True,
            conference__conference_slug__in=linked_event.labels)
    if linked_event.event_style in class_styles:
        general_events = list(chain(
            general_events,
            TicketingEvents.objects.filter(
                include_conference=True,
                conference__conference_slug__in=linked_event.labels)))

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
