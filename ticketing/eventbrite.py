import re
from decimal import Decimal
from eventbrite import Eventbrite
from django.conf import settings
from ticketing.models import (
    EventbriteSettings,
    TicketingEvents,
    TicketItem,
)
from gbetext import (
    eventbrite_error,
    no_settings_error,
    org_id_instructions,
)


def eventbrite_error_create(response):
    from gbe.models import UserMessage
    msg = UserMessage.objects.get_or_create(
        view="SyncTicketItems",
        code="EVENTBRITE_REQUEST_ERROR",
        defaults={'summary': "Error from sending request to eventbrite",
                  'description': eventbrite_error})[0].description
    msg = msg % (response['status_code'], response['error_description'])
    return msg


def setup_eb_api():
    if settings.DEBUG:
        eb_settings = EventbriteSettings.objects.get(system=0)
    else:
        eb_settings = EventbriteSettings.objects.get(system=1)
    eventbrite = Eventbrite(eb_settings.oauth)
    return eventbrite, eb_settings


def load_tickets(eventbrite, ticketing_events=None):
    ti_count = 0
    msg = ""
    if not ticketing_events:
        ticketing_events = TicketingEvents.objects.exclude(
            conference__status="completed")
    for event in ticketing_events:
        has_more_items = True
        continuation_token = ""
        while has_more_items:
            event_response = eventbrite.get(
                '/events/%s/ticket_classes/%s' % (event.event_id,
                                                  continuation_token))
            if 'ticket_classes' not in event_response.keys():
                has_more_items = False
                if event_response['status_code'] != 404:
                    msg = eventbrite_error_create(event_response)
                    return ti_count, msg
            else:
                has_more_items = event_response['pagination']['has_more_items']
                for ticket in event_response['ticket_classes']:
                    ticket_id = re.search(
                        r'\d+',
                        ticket['resource_uri'][::-1]).group()[::-1]
                    if not TicketItem.objects.filter(
                            ticket_id=ticket_id).exists():
                        cost = 0.0
                        if ticket['cost'] is not None:
                            cost = Decimal(re.sub(r'[^\d.]',
                                           '',
                                           ticket['cost']['display']))
                        ticket = TicketItem(
                            ticket_id=ticket_id,
                            title=ticket['name'],
                            cost=cost,
                            modified_by="Eventbrite Import",
                            live=not ticket['hidden'],
                            end_time=ticket['sales_end'],
                            ticketing_event=event)
                        ticket.save()
                        ti_count = ti_count + 1
            if has_more_items:
                continuation_token = "?continuation=%s" % (
                    event_response['pagination']['continuation'])

    return ti_count, msg


def import_eb_ticket_items(events=None):
    '''
    Function is used to initiate an import from ticketing source, returns:
      - a message
      - a is_success boolean false = failure, true = success
    '''
    from gbe.models import UserMessage
    eventbrite = None
    settings = None
    msg = "No message available"
    try:
        eventbrite, settings = setup_eb_api()
    except:
        return UserMessage.objects.get_or_create(
            view="SyncTicketItems",
            code="NO_OAUTH",
            defaults={
                'summary': "Instructions to Set Eventbrite Oauth",
                'description': no_settings_error})[0].description, False
    if settings.organization_id is None:
        org_resp = eventbrite.get('/users/me/organizations/')
        if 'organizations' not in org_resp.keys():
            msg = eventbrite_error_create(org_resp)
        else:
            msg = UserMessage.objects.get_or_create(
                view="SyncTicketItems",
                code="NO_ORGANIZATION",
                defaults={
                    'summary': "Instructions to Set Organization ID",
                    'description': org_id_instructions})[0].description
            for organization in org_resp["organizations"]:
                msg = "%s<br>%s - %s" % (
                    msg,
                    organization['id'],
                    organization['name'])
        return msg, False

    event_count, msg = load_events(eventbrite, settings.organization_id)
    if len(msg) > 0:
        return msg, False
    tickets_count, msg = load_tickets(eventbrite)
    if len(msg) > 0:
        return msg, False
    return "Successfully imported %d events, %d tickets" % (
        event_count,
        tickets_count), True


def load_events(eventbrite, organization_id):
    from gbe.functions import get_current_conference
    has_more_items = True
    continuation_token = ""
    while has_more_items:
        import_item_list = eventbrite.get(
            ('/organizations/%s/events/?order_by=start_asc&' +
             'time_filter=current_future%s') % (organization_id,
                                                continuation_token))
        if 'events' not in import_item_list.keys():
            return 0, eventbrite_error_create(import_item_list)
        has_more_items = import_item_list['pagination']['has_more_items']
        conference = get_current_conference()
        event_count = 0
        for event in import_item_list['events']:
            if not TicketingEvents.objects.filter(event_id=event['id']).exists():
                new_event = TicketingEvents(
                    event_id=event['id'],
                    title=event['name']['text'],
                    description=event['description']['html'],
                    conference=conference)
                new_event.save()
                event_count = event_count + 1
        if has_more_items:
            continuation_token = "&continuation=%s" % (
                import_item_list['pagination']['continuation'])
    return event_count, ""
