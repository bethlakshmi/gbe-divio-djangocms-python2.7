from django.test import TestCase
from django.test import Client
from io import StringIO
from django.core.management import call_command
from mock import patch
from django.contrib.auth.models import User
from tests.factories.ticketing_factories import HumanitixSettingsFactory
from tests.ticketing.ht_event_list import get_events
from tests.ticketing.ht_transactions import (
    order_list,
    complete_trans,
    canceled_trans,
)
from ticketing.models import TicketingEvents, TicketType
from gbetext import import_transaction_message
from tests.functions.gbe_functions import get_limbo
from tests.ticketing.mock_ht_response import MockHTResponse


class TestSyncHTTransactions(TestCase):

    def setUp(self):
        self.client = Client()
        HumanitixSettingsFactory(organiser_id="987654321")

    @patch('requests.get', autospec=True)
    def test_call_command(self, m_humanitix):
        TicketingEvents.objects.all().delete()
        limbo = get_limbo()

        m_humanitix.side_effect = [MockHTResponse(json_data=get_events),
                                   MockHTResponse(json_data=order_list),
                                   MockHTResponse(json_data=complete_trans),
                                   MockHTResponse(json_data=canceled_trans)]
        out = StringIO()
        call_command("sync_ht_transactions", stdout=out)
        response = out.getvalue()
        self.assertIn(
            "Successfully imported 1 events, 6 tickets, 2 packages",
            response)
        self.assertIn("Imported 3 packages and 3 tickets", response)
        self.assertIn("Canceled 1 transactions", response)
