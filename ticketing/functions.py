from itertools import chain
from datetime import datetime
from ticketing.models import (
    TicketingEvents,
    TicketItem,
    TicketPackage,
    TicketType,
)
from ticketing.eventbrite import import_eb_ticket_items
from ticketing.humantix import HumantixClient
from ticketing.brown_paper import import_bpt_ticket_items
from gbetext import class_styles
from django.db.models import Q


def import_ticket_items():
        # Since Eventbrite autosyncs events, we would only need to manually
        # import BPT
        msg = "0"
        is_success = True
        humantix = HumantixClient()
        msg, is_success = import_eb_ticket_items()
        hmsg, his_success = humantix.import_ticket_items()
        count = import_bpt_ticket_items()
        return [(msg, is_success),
                (hmsg, his_success),
                ("BPT: imported %d tickets" % count, True)]


def get_tickets(linked_event):
    # note - the old way didn't seem to care about start/end dates?
    # the new Humanitix way DOES so we can use that when the API lets us.
    general_events = []
    package_query = TicketPackage.objects.filter(
        ticketing_event__conference__conference_slug__in=linked_event.labels,
        live=True,
        has_coupon=False).exclude(
        start_time__gt=datetime.now()).exclude(
        end_time__lt=datetime.now())
    packages = []
    link = None
    if linked_event.event_style not in ["Master", "Volunteer"]:
        general_events = TicketingEvents.objects.filter(
            include_most=True,
            conference__conference_slug__in=linked_event.labels).exclude(
            source=3)
        packages = package_query.filter(whole_shebang=True)
    if linked_event.event_style in class_styles:
        general_events = list(chain(
            general_events,
            TicketingEvents.objects.filter(
                include_conference=True,
                conference__conference_slug__in=linked_event.labels))).exclude(
            source=3)

        packages = package_query.filter(
            Q(conference_only_pass=True) | Q(whole_shebang=True))

    general_events = list(chain(
        general_events,
        TicketingEvents.objects.filter(
            linked_events=linked_event).exclude(
            source=3)))

    ticket_events = []

    for event in general_events:
        if event.live_ticket_count > 0 and event not in ticket_events:
            ticket_events += [event]

    tickets = TicketType.objects.filter(
        linked_events=linked_event,
        live=True,
        has_coupon=False).exclude(
        start_time__gt=datetime.now()).exclude(
        end_time__lt=datetime.now())

    # with Humantix, there is only 1 event, so all links are the same
    if packages.count() > 0:
        link = packages.first().ticketing_event.link
    elif tickets.count() > 0:
        link = tickets.first().ticketing_event.link

    return {"events": ticket_events,
            "link": link,
            "tickets": tickets,
            "packages": packages}


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
