from itertools import chain
from datetime import datetime
from ticketing.models import (
    TicketingEvents,
    TicketItem,
    TicketPackage,
    TicketType,
)
from ticketing.eventbrite import import_eb_ticket_items
from ticketing.humanitix import HumanitixClient
from ticketing.brown_paper import import_bpt_ticket_items
from gbetext import class_styles
from django.db.models import Q


def import_ticket_items():
        # Since Eventbrite autosyncs events, we would only need to manually
        # import BPT
        msg = "0"
        is_success = True
        humanitix = HumanitixClient()
        msg, is_success = import_eb_ticket_items()
        hmsg, his_success = humanitix.import_ticket_items()
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
    tickets = TicketType.objects.filter(
        linked_events=linked_event,
        live=True,
        has_coupon=False).exclude(
        start_time__gt=datetime.now()).exclude(
        end_time__lt=datetime.now())
    packages = package_query.filter(ticket_types__in=tickets)

    link = None
    if linked_event.event_style not in ["Master", "Volunteer"]:
        general_events = TicketingEvents.objects.filter(
            include_most=True,
            conference__conference_slug__in=linked_event.labels).exclude(
            source=3)
        packages = list(chain(packages,
                              package_query.filter(whole_shebang=True)))
    if linked_event.event_style in class_styles:
        general_events = list(chain(
            general_events,
            TicketingEvents.objects.filter(
                include_conference=True,
                conference__conference_slug__in=linked_event.labels).exclude(
                source=3)))

        packages = list(chain(packages, package_query.filter(
            Q(conference_only_pass=True) | Q(whole_shebang=True))))
        tickets = list(chain(tickets, TicketType.objects.filter(
            conference_only_pass=True,
            live=True,
            has_coupon=False).exclude(
            start_time__gt=datetime.now()).exclude(
            end_time__lt=datetime.now())))

    general_events = list(chain(
        general_events,
        TicketingEvents.objects.filter(
            linked_events=linked_event).exclude(
            source=3)))

    ticket_events = []

    for event in general_events:
        if event.live_ticket_count > 0 and event not in ticket_events:
            ticket_events += [event]



    # with Humanitix, there is only 1 event, so all links are the same
    humanitix = HumanitixClient()
    humanitix_active, status_info = humanitix.setup_api()
    if humanitix_active and humanitix.settings.widget_page is not None and (
            len(humanitix.settings.widget_page) > 0):
        link = humanitix.settings.widget_page
    elif len(tickets) > 0:
        link = tickets.first().ticketing_event.link
    elif packages != [] and len(packages) > 0:
        link = packages[0].ticketing_event.link

    if len(ticket_events) > 0 or len(tickets) > 0 or len(packages) > 0:
        return {"events": ticket_events,
                "link": link,
                "tickets": tickets,
                "packages": packages}
    else:
        return None


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
