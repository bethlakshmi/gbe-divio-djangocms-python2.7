import requests
import re
import pytz
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from ticketing.models import (
    EventbriteSettings,
    Purchaser,
    SyncStatus,
    TicketingEvents,
    TicketPackage,
    TicketType,
    Transaction,
)
from gbetext import (
    no_settings_error,
    org_id_instructions,
    import_transaction_message,
    sync_off_instructions,
)
from ticketing.brown_paper import (
    attempt_match_purchaser_to_user,
    match_existing_purchasers_using_email,
)


class HumantixClient:

    # TODO - make into a setting in DB
    settings = {
        'api_key': "c60d691db03f9e8d6276c4fc60e44de39f7fb3fda86f7a3178306e38c7a9c1f2d128074401bfcaad3533078a9e1c045e9f92406698007180968f96526512489d418dc2219c0c40d79fd7df32c1414203067424994730561a051d9b6c2b43768d88fd3f92faf999179732e0003308bd",
        'endpoint': "https://api.humanitix.com"}
    organizer_id = "6568c4ba44bea90207cb28ef"
    import_type = "Humanitix Event"

    def import_ticket_items(self):

        '''
        Function is used to initiate an import from ticketing source, returns:
          - a message
          - a is_success boolean false = failure, true = success
        '''
        eventbrite = None
        settings = None
        msg = "No message available"
        proceed = True

        if not proceed:
            return return_tuple

        load_counts, msg = self.load_events()

        if len(msg) > 0:
            status = SyncStatus(is_success=False,
                                error_msg=msg,
                                import_type=self.import_type,
                                import_number=event_count)
            status.save()
            return msg, False
        else:
            status, created = SyncStatus.objects.get_or_create(
                is_success=True,
                import_type=self.import_type)
            status.import_number = load_counts['events']
            status.save()

        return "Successfully imported %d events, %d tickets, %d packages" % (
            load_counts['events'],
            load_counts['tickettypes'],
            load_counts['ticketpackages']), True


    def load_events(self):
        from gbe.functions import get_current_conference
        has_more_items = True
        event_count = 0
        ticket_count = 0
        package_count = 0
        page = 1
        conference = get_current_conference()
        while has_more_items:
            response = self.perform_api_call('/v1/events', params={
                'page': page,
                'inFutureOnly': 'true',
                })
            if response.status_code != 200 or 'events' not in response.json():
                return 0, self.error_create(response)
            elif len(response.json()['events']) == 0 or (
                    response.json()['total'] < response.json()['pageSize']):
                has_more_items = False
            else:
                page = page + 1

            for event in response.json()['events']:
                if self.organizer_id is None or len(
                        self.organizer_id) == 0 or (
                        event["organiserId"] == self.organizer_id):
                    ticketed_event = None
                    if not TicketingEvents.objects.filter(
                            event_id=event['_id']).exists():
                        ticketed_event = TicketingEvents(
                            event_id=event['_id'],
                            title=event['name'],
                            description=event['description'],
                            conference=conference,
                            source=3)
                        ticketed_event.save()
                        event_count = event_count + 1
                    else:
                        ticketed_event = TicketingEvents.objects.get(
                            event_id=event['_id'])
                    ticket_count = self.load_tickets(
                        event["ticketTypes"],
                        ticketed_event) + ticket_count
                    package_count = self.load_packages(
                        event["packagedTickets"],
                        ticketed_event) + package_count
        return {'events': event_count,
                'tickettypes': ticket_count,
                'ticketpackages': package_count}, ""


    def load_tickets(self, ticketTypes, event):
        ti_count = 0
        for tickettype in ticketTypes:
            if not TicketType.objects.filter(
                    ticket_id=tickettype['_id']).exists():
                ticket = TicketType(
                    ticket_id=tickettype['_id'],
                    title=tickettype['name'],
                    modified_by="Humanitix Import",
                    ticketing_event=event)
                if 'description' in tickettype.keys():
                    ticket.description = tickettype['description']
                ti_count = ti_count + 1
            else:
                ticket = TicketType.objects.get(ticket_id=tickettype['_id'])

            ticket.live = not tickettype['disabled']

            if 'priceRange' in tickettype.keys() and (
                    tickettype['priceRange']['enabled']) and (
                    'min' in tickettype['priceRange'].keys()):
                ticket.cost = tickettype['priceRange']['min']
                ticket.is_minimum = True
            else:
                ticket.cost = tickettype['price']
            ticket.save()

        return ti_count


    def load_packages(self, packages, event):
        ti_count = 0
        for package in packages:
            if not TicketPackage.objects.filter(
                    ticket_id=package['_id']).exists():
                ticket = TicketPackage(
                    ticket_id=package['_id'],
                    title=package['name'],
                    modified_by="Humanitix Import",
                    ticketing_event=event)
                ti_count = ti_count + 1
                if 'description' in package.keys():
                    ticket.description = package['description']
            else:
                ticket = TicketPackage.objects.get(ticket_id=package['_id'])
            
            ticket.live = not package['disabled']
            ticket.cost = package['price']
            ticket.save()

        return ti_count


    def perform_api_call(self, path, params):
        # Basic formatting for all calls to Humantix

        headers = {'x-api-key': self.settings['api_key'],
                   'Accept': 'application/json'}
        full_path = self.settings['endpoint'] + path
        return requests.get(full_path,
                            headers=headers,
                            params=params)


    def error_create(self, response):
        from gbe.models import UserMessage
        msg = UserMessage.objects.get_or_create(
            view="SyncTicketItems",
            code=response['error'],
            defaults={'summary': "Error from sending request to humanitix",
                      'description': response.json()['message']
                      })[0].description
        msg = msg % (response.status_code, response.json()['message'])
        return msg
