from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.ticketing_idd_interface import get_purchased_tickets
from tests.factories.gbe_factories import ProfileFactory
from tests.factories.ticketing_factories import TransactionFactory
import mock


class TestGetPurchasedTickets(TestCase):
    '''Tests for edit_event view'''

    def test_no_purchases(self):
        '''should get no tickets, this person never purchased any
        '''
        elcheapo = ProfileFactory().user_object
        ticket_set = get_purchased_tickets(elcheapo)

        self.assertEqual(ticket_set, [])

    def test_buys_each_year(self):
        '''should get current and upcoming conference tickets, including fees
        '''
        purchase = TransactionFactory()
        purchase.ticket_item.title = "ZZZZ Last Title"
        purchase.ticket_item.save()
        conference = purchase.ticket_item.ticketing_event.conference
        TransactionFactory(
            purchaser=purchase.purchaser,
            ticket_item__ticketing_event__conference=conference)
        TransactionFactory(
            purchaser=purchase.purchaser,
            ticket_item__ticketing_event__conference=conference)
        old_purchase = TransactionFactory(purchaser=purchase.purchaser)
        old_purchase.ticket_item.ticketing_event.conference.status = "ongoing"
        old_purchase.ticket_item.ticketing_event.conference.save()
        ticket_set = get_purchased_tickets(purchase.purchaser.matched_to_user)

        self.assertEqual(len(ticket_set), 2)
        self.assertEqual(ticket_set[0]['conference'].status, "ongoing")
        self.assertEqual(ticket_set[1]['conference'].status, "upcoming")
        self.assertEqual(len(ticket_set[0]['tickets']), 1)
        self.assertEqual(len(ticket_set[1]['tickets']), 3)
