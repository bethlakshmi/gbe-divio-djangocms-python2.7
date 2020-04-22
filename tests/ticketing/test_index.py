from tests.factories.ticketing_factories import (
    TicketItemFactory
)
from ticketing.models import TicketItem
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import (
    index
)
from tests.factories.gbe_factories import (
    UserFactory
)
from django.core.urlresolvers import reverse
from tests.functions.gbe_functions import login_as
from django.contrib.auth.models import User


class TestTicketingIndex(TestCase):
    '''Tests for ticketing index'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.url = reverse('index', urlconf='ticketing.urls')
        self.ticket = TicketItemFactory(live=True,
                                        bpt_event__title="Event Title")

    def test_one_ticket(self):
        '''
           user gets the list
        '''
        response = self.client.get(self.url)
        self.assertContains(response, self.ticket.cost, count=1)

    def test_no_ticket(self):
        '''
           user gets the list
        '''
        TicketItem.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_only_visible_ticket(self):
        '''
           user gets the list
        '''
        not_shown = TicketItemFactory(
            live=False,
            cost=999.99,
            bpt_event__title='This is the Event Title')
        also_not_shown = TicketItemFactory(
            has_coupon=True,
            cost=not_shown.cost,
            bpt_event__title=not_shown.bpt_event)
        ticket = TicketItemFactory(live=True,
                                   bpt_event=not_shown.bpt_event,
                                   cost=123.00)
        response = self.client.get(self.url)
        self.assertContains(response, 'This is the Event Title')
        self.assertNotContains(response, str(not_shown.cost))
        self.assertContains(response, str(ticket.cost))

    def test_not_superuser(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, '<i class="icon-pencil"></i>')

    def test_edit_for_superuser(self):
        superuser = User.objects.create_superuser('ticketing_editor',
                                                  'admin@ticketing.com',
                                                  'secret')
        login_as(superuser, self)
        response = self.client.get(self.url)
        self.assertContains(response, '<i class="icon-pencil"></i>')

    def test_two_prices_one_event(self):
        second_ticket = TicketItemFactory(bpt_event=self.ticket.bpt_event,
                                          cost=self.ticket.cost+10)
        response = self.client.get(self.url)
        assert "$%f - $%f" % (self.ticket.cost, second_ticket.cost)
