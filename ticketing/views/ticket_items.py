from django.shortcuts import render
from django.views.decorators.cache import never_cache
from ticketing.models import TicketingEvents
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    get_ticketable_gbe_events,
    validate_perms,
)
from gbe.models import UserMessage
from gbetext import (
    intro_ticket_assign_message,
    intro_ticket_message,
)
from gbe.ticketing_idd_interface import get_ticket_form
from ticketing.functions import import_ticket_items


@never_cache
def ticket_items(request, conference_choice=None):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    validate_perms(request, ('Ticketing - Admin', ))

    if 'Import' in request.POST:
        import_ticket_items()

    conference_choice = request.GET.get('conference', None)
    if conference_choice:
        events = TicketingEvents.objects.filter(
            conference__conference_slug=conference_choice).order_by('title')
        conference = get_conference_by_slug(conference_choice)
    else:
        events = TicketingEvents.objects.exclude(
            conference__status='completed').order_by('title')
        conference = get_current_conference()
        if conference:
            conference_choice = conference.conference_slug
    intro = UserMessage.objects.get_or_create(
                view="ViewTicketItems",
                code="INTRO_MESSAGE",
                defaults={
                    'summary': "Introduction Message",
                    'description': intro_ticket_message})
    check_intro = UserMessage.objects.get_or_create(
                view="CheckTicketEventItems",
                code="INTRO_MESSAGE",
                defaults={
                    'summary': "Introduction Message",
                    'description': intro_ticket_assign_message})
    gbe_events = get_ticketable_gbe_events(conference_choice)
    context = {'intro': intro[0].description,
               'act_pay_form': get_ticket_form("Act", conference),
               'vendor_pay_form': get_ticket_form("Vendor", conference),
               'act_fees': events.filter(act_submission_event=True),
               'vendor_fees': events.filter(vendor_submission_event=True),
               'open_panel': request.GET.get('open_panel', ""),
               'updated_tickets': eval(
                    request.GET.get('updated_tickets', '[]')),
               'updated_events': eval(request.GET.get('updated_events', '[]')),
               'events': events.filter(act_submission_event=False,
                                       vendor_submission_event=False),
               'conference_slugs': conference_slugs(),
               'conference': conference,
               'check_intro': check_intro[0].description,
               'gbe_events': gbe_events}
    return render(request, r'ticketing/ticket_items.tmpl', context)
