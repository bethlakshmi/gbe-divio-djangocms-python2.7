from itertools import chain
from datetime import datetime
from eventbrite import Eventbrite
from django.conf import settings
from ticketing.models import *
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


def get_eventbrite_price_list(eventbrite, ticketing_events=None):
    ti_list = []
    msg = ""
    if not ticketing_events:
        ticketing_events = TicketingEvents.objects.exclude(
            conference__status="completed")
    for event in ticketing_events:
        event_response = eventbrite.get(
            '/events/%s/ticket_classes/' % event.event_id)
        if 'ticket_classes' not in event_response.keys():
            msg = eventbrite_error_create(event_response)
            return ti_list, msg
        raise Exception(event_response)
    return ti_list, msg


def import_ticket_items(events=None):
    '''
    Function is used to initiate an import from ticketing source, returns:
      - a message
      - a is_success boolean false = failure, true = success
    '''
    from gbe.models import UserMessage
    from gbe.functions import get_current_conference
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

    import_item_list = eventbrite.get(
        '/organizations/%s/events/' % settings.organization_id)
    if 'events' not in import_item_list.keys():
        return eventbrite_error_create(import_item_list)
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
    tickets, msg = get_eventbrite_price_list(eventbrite)
    if len(msg) > 0:
        return msg, False
    for i_item in import_item_list:
        ticket_item, created = TicketItem.objects.get_or_create(
            ticket_id=i_item['ticket_id'],
            defaults=i_item)
        if not created:
            ticket_item.modified_by = 'BPT Import'
            ticket_item.live = i_item['live']
            ticket_item.cost = i_item['cost']
            ticket_item.save()
    return "Successfully imported %d tickets" % len(import_item_list), True


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
        ticketing_event__conference=conference, live=True, has_coupon=False).exclude(
        start_time__gt=datetime.now()).exclude(end_time__lt=datetime.now())
    if bid_type == "Vendor":
        ticket_items = ticket_items.filter(
            ticketing_event__vendor_submission_event=True)
    elif bid_type == "Act":
        ticket_items = ticket_items.filter(
            ticketing_event__act_submission_event=True)
    return ticket_items
