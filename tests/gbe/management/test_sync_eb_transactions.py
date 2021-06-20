from django.test import TestCase
from django.test import Client
from io import StringIO
from django.core.management import call_command
from mock import patch
from django.contrib.auth.models import User
from tests.factories.ticketing_factories import EventbriteSettingsFactory
from tests.ticketing.eb_event_list import event_dict
from tests.ticketing.eb_ticket_list import (
    ticket_dict1,
    ticket_dict2,
    ticket_dict3
)
from tests.ticketing.eb_order_list import order_dict
from ticketing.models import TicketingEvents
from gbetext import import_transaction_message


class TestSyncEBTransactions(TestCase):

    def setUp(self):
        self.client = Client()
        EventbriteSettingsFactory()

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_call_command(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        limbo, created = User.objects.get_or_create(username='limbo')
        m_eventbrite.side_effect = [event_dict,
                                    ticket_dict1,
                                    ticket_dict2,
                                    ticket_dict3,
                                    order_dict,
                                    order_dict,
                                    order_dict]
        out = StringIO()
        call_command("sync_eb_transactions", stdout=out)
        response = out.getvalue()
        self.assertIn(
            "Successfully imported %d events, %d tickets" % (3, 6),
            response)
        self.assertIn(
            "%s  Transactions imported: %d -- Eventbrite" % (
                import_transaction_message,
                1),
            response)
