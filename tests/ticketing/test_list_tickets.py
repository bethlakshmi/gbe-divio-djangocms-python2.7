from django.core.files import File
from ticketing.models import (
    BrownPaperEvents,
    BrownPaperSettings,
    TicketItem
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    BrownPaperSettingsFactory,
    TicketItemFactory
)
from django.test import TestCase
from django.test import Client
from ticketing.views import ticket_items
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
)
from mock import patch, Mock
import urllib
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.urls import reverse
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from datetime import (
    datetime,
    timedelta,
)


class TestListTickets(TestCase):
    '''Tests for ticket_items view'''
    view_name = 'ticket_items'

    def setUp(self):
        self.client = Client()
        self.privileged_user = ProfileFactory.create().\
            user_object
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        self.url = reverse(self.view_name, urlconf='ticketing.urls')

    def import_tickets(self):
        data = {'Import': 'Import'}
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data)
        return response

    def test_list_ticket_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.
        '''
        user = ProfileFactory.create().user_object
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_list_tickets_all_good(self):
        '''
           privileged user gets the list
        '''
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            'No ticket events have been created, use the "Create Event" ' +
            'button above to create some.')

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_inventory(self, m_urlopen):
        '''
           privileged user gets the inventory of tickets from (fake) BPT
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        date_filename = open("tests/ticketing/datelist.xml", 'r')
        price_filename = open("tests/ticketing/pricelist.xml", 'r')
        a.read.side_effect = [File(date_filename).read(),
                              File(price_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)
        ticket = get_object_or_404(
            TicketItem,
            ticket_id='%s-4513068' % (event.bpt_event_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.cost, Decimal('125.00'))

    @patch('urllib.request.urlopen', autospec=True)
    def test_reimport_inventory(self, m_urlopen):
        '''
           privileged user gets the inventory of tickets from (fake) BPT
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        BrownPaperSettingsFactory()
        TicketItemFactory(
            ticket_id='%s-4513068' % (event.bpt_event_id),
            has_coupon=True,
            live=False,
            bpt_event=event)
        a = Mock()
        date_filename = open("tests/ticketing/datelist.xml", 'r')
        price_filename = open("tests/ticketing/pricelist.xml", 'r')
        a.read.side_effect = [File(date_filename).read(),
                              File(price_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)
        ticket = get_object_or_404(
            TicketItem,
            ticket_id='%s-4513068' % (event.bpt_event_id))
        assert ticket.live
        assert ticket.has_coupon

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_event_detail(self, m_urlopen):
        '''
           privileged user gets the inventory of tickets from (fake) BPT
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory(title='', description='')
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        date_filename = open("tests/ticketing/datelist.xml", 'r')
        price_filename = open("tests/ticketing/pricelist.xml", 'r')
        a.read.side_effect = [File(event_filename).read(),
                              File(date_filename).read(),
                              File(price_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)
        reload_event = get_object_or_404(
            BrownPaperEvents,
            bpt_event_id='%s' % (event.bpt_event_id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The Great Burlesque Exposition of 2016 takes place Feb. 5-7",
            reload_event.description)

    def test_get_no_inventory(self):
        '''
           privileged user gets the inventory of tickets with no tickets
        '''
        BrownPaperEvents.objects.all().delete()
        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_event_list(self, m_urlopen):
        '''
           not event list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory(title="", description="")
        BrownPaperSettingsFactory()

        a = Mock()
        a.read.side_effect = []
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_date_list(self, m_urlopen):
        '''
           not date list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory(title="", description="")
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        a.read.side_effect = [File(event_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_price_list(self, m_urlopen):
        '''
           not price list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory(title="", description="")
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        date_filename = open("tests/ticketing/datelist.xml", 'r')
        a.read.side_effect = [File(event_filename).read(),
                              File(date_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_urlerror(self, m_urlopen):
        '''
           first read from BPT has a URL read error
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory(title="", description="")
        BrownPaperSettingsFactory()

        a = Mock()
        a.read.side_effect = urllib.error.URLError("test url error")
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_settings(self, m_urlopen):
        '''
           not date list comes when getting inventory
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory(title="", description="")

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        a.read.side_effect = [File(event_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    def test_list_tickets_for_conf(self):
        '''
           privileged user gets the list for a conference
        '''
        ticket = TicketItemFactory()
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={"conference": ticket.bpt_event.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Conference Classes")
        self.assertNotContains(response, "fas fa-check")

    def test_ticket_active_state(self):
        '''
           privileged user gets the list for a conference
        '''
        active_ticket = TicketItemFactory(live=True)
        not_live_ticket = TicketItemFactory(
            live=False,
            bpt_event=active_ticket.bpt_event)
        coupon_ticket = TicketItemFactory(
            has_coupon=True,
            live=True,
            bpt_event=active_ticket.bpt_event)

        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, data={
            "conference": active_ticket.bpt_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible')
        self.assertContains(response, 'Hidden')
        self.assertContains(response, 'Requires Coupon')
        self.assertContains(response, 'Regular Fee', 3)

    def test_ticket_currently_active(self):
        '''
           privileged user gets the list for a conference
        '''
        active_ticket = TicketItemFactory(
            live=True,
            start_time=datetime.now()-timedelta(days=1),
            end_time=datetime.now()+timedelta(days=1))

        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, data={
            "conference": active_ticket.bpt_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            active_ticket.start_time.strftime('%m/%d/%Y'))
        self.assertContains(
            response,
            active_ticket.end_time.strftime('%m/%d/%Y'))

    def test_ticket_active_donation(self):
        '''
           privileged user gets the list for a conference
        '''
        active_ticket = TicketItemFactory(live=True, is_minimum=True)

        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url, data={
            "conference": active_ticket.bpt_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible')
        self.assertContains(response, 'Minimum Donation')

    def test_ticket_includes_conference(self):
        active_ticket = TicketItemFactory(live=True,
                                          bpt_event__include_conference=True)
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Conference Classes")
        self.assertContains(response, "fas fa-check")
        self.assertNotContains(response, "set_ticket_to_event")
        self.assertContains(
            response,
            "To change, edit ticket and remove 'Includes Most' or " +
            "'Includes Conference'")
        self.assertContains(response, "Includes all Conference Classes")

    def test_ticket_includes_most(self):
        active_ticket = TicketItemFactory(live=True,
                                          bpt_event__include_most=True)
        gbe_event = ShowFactory(
            e_conference=active_ticket.bpt_event.conference)
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Conference Classes")
        self.assertContains(response, gbe_event.e_title)
        self.assertContains(response, "fas fa-check", 2)
        self.assertNotContains(response, "set_ticket_to_event")
        self.assertContains(
            response,
            "To change, edit ticket and remove 'Includes Most'")
        self.assertContains(
            response,
            "To change, edit ticket and remove 'Includes Most' or " +
            "'Includes Conference'")
        self.assertContains(response,
                            "Includes all events except Master Classes")

    def test_ticket_linked_event(self):
        active_ticket = TicketItemFactory(live=True)
        gbe_event = ShowFactory(
            e_conference=active_ticket.bpt_event.conference)
        active_ticket.bpt_event.linked_events.add(gbe_event)
        active_ticket.bpt_event.save()
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
