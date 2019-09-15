from itertools import chain


def get_tickets(linked_event, most=False, conference=False):
    from ticketing.models import BrownPaperEvents

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
