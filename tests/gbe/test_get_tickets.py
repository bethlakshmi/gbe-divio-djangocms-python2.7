from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
import mock
from tests.factories.gbe_factories import (
    ClassFactory,
    GenericEventFactory,
    ShowFactory
)
from tests.factories.ticketing_factories import (
    TicketingEventsFactory,
    TicketItemFactory
)
from ticketing.models import TicketingEvents


class TestGetTickets(TestCase):
    '''Tests for edit_event view'''

    def setUp(self):
        TicketingEvents.objects.all().delete()

    def test_get_tickets_for_volunteer_opp(self):
        '''should get no tickets, volunteer opportunities are free
        '''
        event = GenericEventFactory()
        tickets = event.get_tickets()

        self.assertEqual(tickets, [])

    def test_get_tickets_for_master_class(self):
        '''get the one ticket that is active for the Master Class
        '''
        event = GenericEventFactory(
            type='Master')
        ticketing_event = TicketingEventsFactory(conference=event.e_conference,
                                                 title="Master Class 2017")
        ticketing_event.linked_events.add(event)
        ticketing_event.save()
        TicketItemFactory(ticketing_event=ticketing_event,
                          live=True,
                          has_coupon=False)
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[0].title,
            "Master Class 2017")

    def test_get_tickets_for_special_event(self):
        '''get the one ticket that is active for all except master classes
        '''
        event = GenericEventFactory(
            type='Special')
        ticketing_event = TicketingEventsFactory(
            conference=event.e_conference,
            include_most=True,
            title="The Whole Shebang 2016")
        TicketItemFactory(ticketing_event=ticketing_event,
                          live=True,
                          has_coupon=False)

        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[0].title,
            "The Whole Shebang 2016")

    def test_get_tickets_for_class(self):
        '''get one ticket for everything but master, and one for classes
        '''
        event = ClassFactory()
        ws_ticketing_event = TicketingEventsFactory(
            conference=event.e_conference,
            include_most=True,
            title="The Whole Shebang 2016")
        sch_ticketing_event = TicketingEventsFactory(
            conference=event.e_conference,
            include_conference=True,
            title="The Scholar 2016")
        whole_shebang = TicketItemFactory(
            ticketing_event=ws_ticketing_event,
            live=True,
            has_coupon=False)
        scholar = TicketItemFactory(
            ticketing_event=sch_ticketing_event,
            live=True,
            has_coupon=False)
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 2)
        self.assertEqual(
            tickets[0],
            ws_ticketing_event)
        self.assertEqual(
            tickets[1],
            sch_ticketing_event)

    def test_get_tickets_for_show(self):
        '''just gets 1 ticket for Whole Shebang
        '''
        event = ShowFactory()
        ticketing_event = TicketingEventsFactory(
            conference=event.e_conference,
            include_most=True,
            title="The Whole Shebang 2016")
        TicketItemFactory(ticketing_event=ticketing_event,
                          live=True,
                          has_coupon=False)
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[0].title,
            "The Whole Shebang 2016")

    def test_get_tickets_for_class_three_ways(self):
        '''the ticket is linked to the class event three ways - 'most',
        'conference', and a direct link.  It only should appear once.
        '''
        event = ClassFactory()
        ticketing_event = TicketingEventsFactory(
            conference=event.e_conference,
            include_most=True,
            include_conference=True,
            title="The Whole Shebang 2016")
        ticketing_event.linked_events.add(event)
        ticketing_event.save()
        TicketItemFactory(ticketing_event=ticketing_event,
                          live=True,
                          has_coupon=False)

        tickets = event.get_tickets()
        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[0].title,
            "The Whole Shebang 2016")

    def test_get_tickets_nothing_active(self):
        '''the ticket is linked to the class and there are two active prices
        only the most expensive is shown
        '''
        event = ClassFactory()
        ticketing_event = TicketingEventsFactory(
            conference=event.e_conference,
            include_conference=True)
        TicketItemFactory(ticketing_event=ticketing_event,
                          live=False,
                          has_coupon=False,
                          title="The Whole Shebang 2016")
        TicketItemFactory(ticketing_event=ticketing_event,
                          live=True,
                          has_coupon=True,
                          cost=299.99,
                          title="The Whole Shebang 2016 - expensive")

        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 0)
