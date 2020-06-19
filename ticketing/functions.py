from ticketing.models import (
    BrownPaperEvents,
    TicketItem,
)
from itertools import chain
from datetime import datetime
from ticketing.brown_paper import get_bpt_price_list


def import_ticket_items(events=None):
    '''
    Function is used to initiate an import from BPT or other sources of
    new Ticket Items.  It will not override existing items.
    '''
    import_item_list = get_bpt_price_list(events)

    for i_item in import_item_list:
        ticket_item, created = TicketItem.objects.get_or_create(
            ticket_id=i_item['ticket_id'],
            defaults=i_item)
        if not created:
            ticket_item.modified_by = 'BPT Import'
            ticket_item.live = i_item['live']
            ticket_item.cost = i_item['cost']
            ticket_item.save()
    return len(import_item_list)

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
