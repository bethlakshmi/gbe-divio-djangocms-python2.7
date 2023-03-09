import re
import pytz
from datetime import datetime
from decimal import Decimal
from eventbrite import Eventbrite
from django.conf import settings
from django.contrib.auth.models import User
from ticketing.models import (
    EventbriteSettings,
    Purchaser,
    SyncStatus,
    TicketingEvents,
    TicketItem,
    Transaction,
)
from gbetext import (
    eventbrite_error,
    no_settings_error,
    org_id_instructions,
    import_transaction_message,
    sync_off_instructions,
)
from ticketing.brown_paper import (
    attempt_match_purchaser_to_user,
    match_existing_purchasers_using_email,
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
    from gbe.models import UserMessage
    system_state = 1
    eb_settings = None
    eventbrite = None
    if settings.DEBUG:
        system_state = 0
    if EventbriteSettings.objects.filter(system=system_state).exists():
        eb_settings = EventbriteSettings.objects.get(system=system_state)
        eventbrite = Eventbrite(eb_settings.oauth)
    else:
        return False, (UserMessage.objects.get_or_create(
            view="SyncTicketItems",
            code="NO_OAUTH",
            defaults={
                'summary': "Instructions to Set Eventbrite Oauth",
                'description': no_settings_error}
            )[0].description, False), None, None

    if not eb_settings.active_sync:
        return False, (UserMessage.objects.get_or_create(
            view="SyncTicketItems",
            code="SYNC_OFF",
            defaults={
                'summary': "Ticketing Sync is OFF",
                'description': sync_off_instructions}
            )[0].description % "Eventbrite", True), None, None
    if eb_settings.organization_id is None:
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
        return False, (msg, False), None, None

    return True, ("", ""), eventbrite, eb_settings


def get_cost(eb_entity):
    cost = 0.0
    if eb_entity is not None:
        cost = Decimal(re.sub(r'[^\d.]', '', eb_entity['display']))
    return cost


def load_tickets(eventbrite):
    ti_count = 0
    msg = ""
    ticketing_events = TicketingEvents.objects.exclude(
        conference__status="completed").filter(source=2)
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
                        ticket = TicketItem(
                            ticket_id=ticket_id,
                            title=ticket['name'],
                            cost=get_cost(ticket['cost']),
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


def load_events(eventbrite, organization_id):
    from gbe.functions import get_current_conference
    has_more_items = True
    continuation_token = ""
    event_count = 0
    while has_more_items:
        import_item_list = eventbrite.get(
            ('/organizations/%s/events/?order_by=start_asc&' +
             'time_filter=current_future%s') % (organization_id,
                                                continuation_token))
        if 'events' not in import_item_list.keys():
            return 0, eventbrite_error_create(import_item_list)
        has_more_items = import_item_list['pagination']['has_more_items']
        conference = get_current_conference()
        for event in import_item_list['events']:
            if not TicketingEvents.objects.filter(
                    event_id=event['id']).exists():
                new_event = TicketingEvents(
                    event_id=event['id'],
                    title=event['name']['text'],
                    description=event['description']['html'],
                    conference=conference,
                    source=2)
                new_event.save()
                event_count = event_count + 1
        if has_more_items:
            continuation_token = "&continuation=%s" % (
                import_item_list['pagination']['continuation'])
    return event_count, ""


def import_eb_ticket_items():
    '''
    Function is used to initiate an import from ticketing source, returns:
      - a message
      - a is_success boolean false = failure, true = success
    '''
    eventbrite = None
    settings = None
    msg = "No message available"

    proceed, return_tuple, eventbrite, settings = setup_eb_api()
    if not proceed:
        return return_tuple
    event_count, msg = load_events(eventbrite, settings.organization_id)
    if len(msg) > 0:
        status = SyncStatus(is_success=False,
                            error_msg=msg,
                            import_type="EB Event",
                            import_number=event_count)
        status.save()
        return msg, False
    else:
        status, created = SyncStatus.objects.get_or_create(
            is_success=True,
            import_type="EB Event")
        status.import_number = event_count
        status.save()

    tickets_count, msg = load_tickets(eventbrite)
    if len(msg) > 0:
        status = SyncStatus(is_success=False,
                            error_msg=msg,
                            import_type="EB Ticket",
                            import_number=tickets_count)
        status.save()
        return msg, False
    else:
        status, created = SyncStatus.objects.get_or_create(
            is_success=True,
            import_type="EB Ticket")
        status.import_number = tickets_count
        status.save()

    return "Successfully imported %d events, %d tickets" % (
        event_count,
        tickets_count), True


def process_eb_purchases():
    '''
    Used to get the list of current orders in eventbrite and update the
    transaction table accordingly.

    Returns: the number of transactions imported.
    '''
    count = 0
    from gbe.models import UserMessage
    eventbrite = None
    settings = None
    msgs = []
    proceed, return_tuple, eventbrite, settings = setup_eb_api()

    if not proceed:
        return [return_tuple]

    # sync up any prior purchasers who may have setup accounts after purchase
    match_existing_purchasers_using_email()

    for event in TicketingEvents.objects.exclude(
            conference__status='completed').filter(source=2):
        has_more_items = True
        continuation_token = ""
        while has_more_items:
            import_list = eventbrite.get(
                ('/events/%s/attendees/?%s') % (
                    event.event_id,
                    continuation_token))
            if 'attendees' not in import_list.keys():
                has_more_items = False
                eb_msg = eventbrite_error_create(import_list)
                msgs += [(eb_msg, False)]
                status = SyncStatus(
                    is_success=False,
                    error_msg=eb_msg,
                    import_type="EB Transaction")
                status.save()
            else:
                has_more_items = import_list['pagination']['has_more_items']
                for attendee in import_list['attendees']:
                    if attendee['status'].lower() == "attending":
                        save_msg, is_success = eb_save_orders_to_database(
                            event.event_id,
                            attendee)
                    elif attendee['status'].lower() == "not attending":
                        save_msg, is_success = eb_remove_orders_in_database(
                            event.event_id,
                            attendee)
                    else:
                        print(attendee)
                        is_success = True

                    if not is_success:
                        msgs += [(save_msg, False)]

                        status = SyncStatus(is_success=False,
                                            error_msg=save_msg,
                                            import_type="EB Transaction")
                        status.save()
                    else:
                        count = save_msg + count
                if has_more_items:
                    continuation_token = "&continuation=%s" % (
                        import_list['pagination']['continuation'])

    success_msg = UserMessage.objects.get_or_create(
            view="ViewTransactions",
            code="IMPORT_EB_MESSAGE",
            defaults={'summary': "Import EB Transactions Message",
                      'description': import_transaction_message})
    msg = "%s  Transactions imported: %d -- Eventbrite" % (
        success_msg[0].description,
        count)
    status, created = SyncStatus.objects.get_or_create(
        is_success=True,
        import_type="EB Transaction")
    status.import_number = count
    status.save()
    msgs += [(msg, True)]
    return msgs


def eb_remove_orders_in_database(event_id, attendee):
    '''
    Function takes an object from the eventbrite order list call and
    REMOVES the transaction object, because it's a refund/cancellation.

    event_id - the ID of the event associated to this order
    order - the order object from the EB call
    Returns:  the Transaction object.  May throw an exception.
    '''
    attendee_count = 0
    if Transaction.objects.filter(reference=attendee['id']).exists():
        trans = Transaction.objects.filter(reference=attendee['id'])
        trans.delete()
        attendee_count = attendee_count + 1

    return attendee_count, True

def eb_save_orders_to_database(event_id, attendee):
    '''
    Function takes an object from the eventbrite order list call and
    builds an equivalent transaction object.

    event_id - the ID of the event associated to this order
    order - the order object from the EB call
    Returns:  the Transaction object.  May throw an exception.
    '''
    attendee_count = 0
    if not Transaction.objects.filter(reference=attendee['id']):
        trans = Transaction()

        if not TicketItem.objects.filter(
                ticket_id=attendee['ticket_class_id']).exists():
            # it's ok this is terminal, it's the lowest layer of loop
            return "Ticket Item for id %s does not exist" % (
                attendee['ticket_class_id']), False

        trans.ticket_item = TicketItem.objects.get(
            ticket_id=attendee['ticket_class_id'])
        trans.amount = get_cost(attendee['costs']['base_price'])

        # Build a purchaser object.
        if Purchaser.objects.filter(
                email=attendee['profile']['email']).exists():
            purchaser = Purchaser.objects.filter(
                email=attendee['profile']['email']).order_by('-pk').first()
        else:
            purchaser = Purchaser(
                email=attendee['profile']['email'],
                first_name=attendee['profile']['first_name'],
                last_name=attendee['profile']['last_name'])

            # assign to a user or limbo
            matched_user = attempt_match_purchaser_to_user(purchaser)
            if matched_user is None:
                purchaser.matched_to_user = User.objects.get(username='limbo')
            else:
                purchaser.matched_to_user = matched_user
            purchaser.save()

        # Build out the remainder of the transaction.
        trans.purchaser = purchaser
        trans.order_date = pytz.utc.localize(
            datetime.strptime(
                attendee['created'],
                "%Y-%m-%dT%H:%M:%SZ"))
        trans.order_notes = attendee['ticket_class_name']
        trans.reference = attendee['id']
        trans.payment_source = 'Eventbrite'
        trans.shipping_method = attendee['delivery_method']

        trans.save()
        attendee_count = attendee_count + 1
    return attendee_count, True
