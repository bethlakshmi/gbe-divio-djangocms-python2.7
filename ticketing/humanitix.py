import requests
import re
import pytz
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from ticketing.models import (
    HumanitixSettings,
    Purchaser,
    SyncStatus,
    TicketingEvents,
    TicketPackage,
    TicketType,
    Transaction,
)
from gbetext import (
    no_ht_settings_error,
    import_transaction_message,
    sync_off_instructions,
)
from ticketing.brown_paper import (
    attempt_match_purchaser_to_user,
    match_existing_purchasers_using_email,
)


class HumanitixClient:
    import_type = "Humanitix Event"
    settings = None

    def setup_api(self):
        from gbe.models import UserMessage
        system_state = 1
        if settings.DEBUG:
            system_state = 0
        if HumanitixSettings.objects.filter(system=system_state).exists():
            self.settings = HumanitixSettings.objects.get(system=system_state)
        else:
            return False, (UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_OAUTH",
                defaults={
                    'summary': "Instructions to Set Humanitix API token",
                    'description': no_ht_settings_error}
                )[0].description, False)

        if not self.settings.active_sync:
            return False, (UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SYNC_OFF",
                defaults={
                    'summary': "Ticketing Sync is OFF",
                    'description': sync_off_instructions}
                )[0].description % "Humanitix", True)
        return True, ("", "")

    def process_transactions(self):
        msgs = []
        proceed, return_tuple = self.setup_api()
        if not proceed:
            return [return_tuple]
        # sync up any prior purchasers who may have setup accounts
        match_existing_purchasers_using_email()

        for event in TicketingEvents.objects.exclude(
                conference__status='completed').filter(source=3):
            orders, is_success = self.get_orders(event)
            
            # we're done if there's no orders
            if is_success and len(orders) > 0:
                msgs = msgs + self.get_order_inventory(event, orders)
                msgs = msgs + self.get_cancellations(event)
            else:
                msgs += [(orders, is_success)]
        return msgs

    def get_cancellations(self, event):
        # return a tuple (A, B) where A = the result or a message on why this
        # failed, and B is whether processing halted early due to error
        page = 1
        has_more_items = True
        num_cancelled = 0
        msgs = []
        while has_more_items:
            response = self.perform_api_call(
                '/v1/events/%s/tickets' % event.event_id,
                params={'page': page,
                        'status': 'cancelled'})

            if response.status_code != 200 or 'tickets' not in response.json():
                msg = self.error_create(response)
                status = SyncStatus(
                    is_success=False,
                    error_msg=msg,
                    import_type="HT Cancellations")
                status.save()
                return [msg, False]
            elif len(response.json()['tickets']) == 0 or (
                    response.json()['total'] < response.json()['pageSize']):
                has_more_items = False
            else:
                page = page + 1

            for ticket in response.json()['tickets']:
                # packages are traced by packageGroupId
                if 'packageGroupId' in ticket.keys():
                    reference = ticket['packageGroupId']
                # ticket types are traced by _id
                else:
                    reference = ticket['_id']

                if Transaction.objects.filter(
                        reference=reference,
                        ticket_item__ticketing_event__source=3).exclude(
                        status="canceled").exists():
                    trans = Transaction.objects.get(
                        reference=reference,
                        ticket_item__ticketing_event__source=3)
                    trans.status = "canceled"
                    trans.import_date = timezone.now()
                    trans.save()
                    num_cancelled = num_cancelled + 1
        msgs += [("Canceled %d transactions" % (num_cancelled), True)]
        status = SyncStatus(is_success=True,
                            import_type="HT Cancellations",
                            import_number=num_cancelled)
        status.save()
        return msgs

    def get_order_inventory(self, event, orders):
        # return a tuple (A, B) where A = the result or a message on why this
        # failed, and B is whether processing halted early due to error
        page = 1
        has_more_items = True
        num_added_tics = 0
        num_added_pkgs = 0
        msgs = []
        while has_more_items:
            response = self.perform_api_call(
                '/v1/events/%s/tickets' % event.event_id,
                params={'page': page,
                        'status': 'complete'})

            if response.status_code != 200 or 'tickets' not in response.json():
                msg = self.error_create(response)
                status = SyncStatus(
                    is_success=False,
                    error_msg=msg,
                    import_type="HT Transaction")
                status.save()
                return [msg, False]
            elif len(response.json()['tickets']) == 0 or (
                    response.json()['total'] < response.json()['pageSize']):
                has_more_items = False
            else:
                page = page + 1

            for ticket in response.json()['tickets']:
                # common elements if we need to make transaction
                trans = Transaction(
                    order_date=pytz.utc.localize(datetime.strptime(
                        ticket['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")),
                    payment_source='Humanitix')
                # packages are traced by packageGroupId
                if 'packageGroupId' in ticket.keys():

                    if not Transaction.objects.filter(
                            reference=ticket['packageGroupId']).exists():
                        if not TicketPackage.objects.filter(
                               ticket_id=ticket['packageId']).exists():
                            msgs += [("Package for id %s does not exist" % (
                                ticket['packageId']), False)]
                        else:
                            trans.reference = ticket['packageGroupId']
                            trans.ticket_item = TicketPackage.objects.get(
                                    ticket_id=ticket['packageId'])
                            trans.purchaser=self.setup_purchaser(
                                    orders[ticket['orderId']])
                            trans.save()
                            num_added_pkgs = num_added_pkgs + 1
                # ticket types are traced by _id
                else:
                    if not Transaction.objects.filter(
                            reference=ticket['_id']).exists():
                        if not TicketType.objects.filter(
                               ticket_id=ticket['ticketTypeId']).exists():
                            msgs += [("Ticket Type for id %s does not exist" % (
                                ticket['ticketTypeId']), False)]
                        else:
                            trans.reference = ticket['_id']
                            trans.ticket_item=TicketType.objects.get(
                                ticket_id=ticket['ticketTypeId'])
                            trans.purchaser=self.setup_purchaser(
                                orders[ticket['orderId']])
                            trans.save()
                            num_added_tics = num_added_tics + 1
        msgs += [("Imported %d packages and %d tickets" % (
            num_added_pkgs,
            num_added_tics), True)]
        status = SyncStatus(is_success=True,
                            import_type="HT Transaction",
                            import_number=num_added_pkgs + num_added_tics)
        status.save()
        return msgs

    def get_orders(self, event):
        # return a tuple (A, B) where A = the result or a message on why this
        # failed, and B is whether processing halted early due to error
        orders = {}
        page = 1
        has_more_items = True
        while has_more_items:
            response = self.perform_api_call(
                '/v1/events/%s/orders' % event.event_id,
                params={'page': page})

            if response.status_code != 200 or 'orders' not in response.json():
                msg = self.error_create(response)
                status = SyncStatus(
                    is_success=False,
                    error_msg=msg,
                    import_type="HT Transaction")
                status.save()
                return (msg, False)
            elif len(response.json()['orders']) == 0 or (
                    response.json()['total'] < response.json()['pageSize']):
                has_more_items = False
            else:
                page = page + 1

            for order in response.json()['orders']:
                orders[order['_id']] = {
                    'email': order['email'],
                    'first_name': order['firstName'],
                    'last_name': order['lastName']}

        return (orders, True)

    def import_ticket_items(self):

        '''
        Function is used to initiate an import from ticketing source, returns:
          - a message
          - a is_success boolean false = failure, true = success
        '''
        msg = "No message available"

        proceed, return_tuple = self.setup_api()
        if not proceed:
            return return_tuple

        load_counts, msg = self.load_events()

        if len(msg) > 0:
            status = SyncStatus(is_success=False,
                                error_msg=msg,
                                import_type=self.import_type,
                                import_number=load_counts['events'])
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
                return ({'events': 0, 'tickettypes': 0, 'ticketpackages': 0},
                        self.error_create(response))
            elif len(response.json()['events']) == 0 or (
                    response.json()['total'] < response.json()['pageSize']):
                has_more_items = False
            else:
                page = page + 1

            for event in response.json()['events']:
                if self.settings.organiser_id is None or len(
                        self.settings.organiser_id) == 0 or (
                        event["organiserId"] == self.settings.organiser_id):
                    ticketed_event = None
                    if not TicketingEvents.objects.filter(
                            event_id=event['_id']).exists():
                        ticketed_event = TicketingEvents(
                            event_id=event['_id'],
                            title=event['name'],
                            description=event['description'],
                            conference=conference,
                            slug=event['slug'],
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
                    ticketing_event=event,
                    live=not tickettype['disabled'])
                if 'description' in tickettype.keys():
                    ticket.description = tickettype['description']
                ti_count = ti_count + 1
            else:
                ticket = TicketType.objects.get(ticket_id=tickettype['_id'])

            if 'price' in tickettype.keys():
                ticket.cost = tickettype['price']

            if 'priceRange' in tickettype.keys() and (
                    tickettype['priceRange']['enabled']):
                if 'min' in tickettype['priceRange'].keys():
                    ticket.cost = tickettype['priceRange']['min']
                ticket.is_minimum = True
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
                    ticketing_event=event,
                    live=not package['disabled'])
                ti_count = ti_count + 1
                if 'description' in package.keys():
                    ticket.description = package['description']
            else:
                ticket = TicketPackage.objects.get(ticket_id=package['_id'])

            ticket.cost = package['price']
            ticket.save()

            ticket.ticket_types.clear()
            for ticket_type in package['tickets']:
                # NOTE - not finding a tickettype is a silent error.
                if TicketType.objects.filter(
                        ticket_id=ticket_type['ticketTypeId']).exists():
                    ticket.ticket_types.add(TicketType.objects.get(
                        ticket_id=ticket_type['ticketTypeId']))

        return ti_count

    def setup_purchaser(self, order):
        purchaser = None
        if Purchaser.objects.filter(email=order['email']).exists():
            purchaser = Purchaser.objects.filter(
                email=order['email']).order_by('-pk').first()
        else:
            purchaser = Purchaser(
                email=order['email'],
                first_name=order['first_name'],
                last_name=order['last_name'])

        # assign to a user or limbo
        matched_user = attempt_match_purchaser_to_user(purchaser)
        if matched_user is None:
            purchaser.matched_to_user = User.objects.get(username='limbo')
        else:
            purchaser.matched_to_user = matched_user
        purchaser.save()
        return purchaser

    def perform_api_call(self, path, params):
        # Basic formatting for all calls to Humantix

        headers = {'x-api-key': self.settings.api_key,
                   'Accept': 'application/json'}
        full_path = self.settings.endpoint + path
        return requests.get(full_path,
                            headers=headers,
                            params=params)

    def error_create(self, response):
        from gbe.models import UserMessage
        msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code=response.json()['error'],
            defaults={'summary': "Error from sending request to humanitix",
                      'description': response.json()['message']
                      })[0].description
        msg = response.json()['error'] + ' - ' + msg
        return msg
