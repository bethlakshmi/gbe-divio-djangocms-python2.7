import copy
import eventbrite
from django.core.files import File
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch, Mock
import urllib
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.urls import reverse
from ticketing.models import (
    TicketingEvents,
    BrownPaperSettings,
    TicketItem
)
from tests.factories.ticketing_factories import (
    BrownPaperSettingsFactory,
    EventbriteSettingsFactory,
    TicketItemFactory,
    TicketingEventsFactory,
)
from tests.factories.gbe_factories import ProfileFactory
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    SchedEventFactory,
)
from gbetext import (
    eventbrite_error,
    no_settings_error,
    org_id_instructions,
)
from tests.ticketing.eb_event_list import event_dict
from tests.ticketing.eb_ticket_list import (
    ticket_dict1,
    ticket_dict2,
    ticket_dict3
)
from tests.ticketing.eb_organizations import org_dict
from tests.functions.gbe_functions import (
    assert_alert_exists,
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
        self.privileged_user = ProfileFactory.create().\
            user_object
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        self.url = reverse(self.view_name, urlconf='ticketing.urls')

    def import_tickets(self):
        data = {'Import': 'Import'}
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data)
        return response

    @override_settings(DEBUG=True)
    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_debug_server(self, m_eventbrite):
        # test case for debug server being different, w no events to sync
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
        EventbriteSettingsFactory(system=0)
        empty_event_dict = copy.deepcopy(event_dict)
        empty_event_dict['events'] = []
        m_eventbrite.side_effect = [empty_event_dict]

        response = self.import_tickets()
        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported %d events, %d tickets") % (0, 0))
        assert_alert_exists(response, 'success', 'Success', (
            "BPT: imported %d tickets") % (0))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_no_org(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory(organization_id=None)

        m_eventbrite.side_effect = [org_dict]

        response = self.import_tickets()
        assert_alert_exists(
            response,
            'danger',
            'Error',
            "%s<br>%s - %s" % (org_id_instructions, "547440371489", "GBE Dev"))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_org_fail(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory(organization_id=None)

        m_eventbrite.side_effect = [{
            "status_code": 403,
            "error_description": "Made up error",
            "error": "NOT_ALLOWED"}]

        response = self.import_tickets()
        assert_alert_exists(
            response,
            'danger',
            'Error',
            eventbrite_error % (403, "Made up error"))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_inventory_no_organizer(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()

        m_eventbrite.side_effect = [event_dict,
                                    ticket_dict1,
                                    ticket_dict2,
                                    ticket_dict3]

        response = self.import_tickets()
        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported %d events, %d tickets") % (3, 6))
        assert_alert_exists(response, 'success', 'Success', (
            "BPT: imported %d tickets") % (0))
        ticket = get_object_or_404(TicketItem, ticket_id='987987987')
        self.assertEqual(ticket.cost, Decimal('0.00'))
        ticket = get_object_or_404(TicketItem, ticket_id='098098098')
        self.assertEqual(ticket.cost, Decimal('100.00'))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_inventory_filter_organizer(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory(organizer_id="33556727241")

        m_eventbrite.side_effect = [event_dict,
                                    ticket_dict2]

        response = self.import_tickets()
        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported %d events, %d tickets") % (1, 2))
        assert_alert_exists(response, 'success', 'Success', (
            "BPT: imported %d tickets") % (0))
        ticket = get_object_or_404(TicketItem, ticket_id='890890890')
        self.assertEqual(ticket.cost, Decimal('0.00'))
        ticket = get_object_or_404(TicketItem, ticket_id='3255985')
        self.assertEqual(ticket.cost, Decimal('100.00'))
        self.assertTrue(TicketingEvents.objects.filter(
            event_id='2222333332323232').exists())
        self.assertFalse(TicketingEvents.objects.filter(
            event_id='44454545454545454').exists())

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_inventory_ticket_pagination(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        simple_event_dict = copy.deepcopy(event_dict)
        simple_event_dict['events'] = [event_dict['events'][0]]
        continue_ticket_page = copy.deepcopy(ticket_dict1)
        continue_ticket_page['pagination']['has_more_items'] = True
        continue_ticket_page['pagination']['continuation'] = "eyJwYWdlIjogMn0"
        m_eventbrite.side_effect = [simple_event_dict,
                                    continue_ticket_page,
                                    ticket_dict3]

        response = self.import_tickets()
        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported %d events, %d tickets" % (1, 4)))
        assert_alert_exists(response, 'success', 'Success', (
            "BPT: imported %d tickets") % (0))
        ticket = get_object_or_404(TicketItem, ticket_id='987987987')
        self.assertEqual(ticket.cost, Decimal('0.00'))
        ticket = get_object_or_404(TicketItem, ticket_id='098098098')
        self.assertEqual(ticket.cost, Decimal('100.00'))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_inventory_ticket_fail(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        simple_event_dict = copy.deepcopy(event_dict)
        simple_event_dict['events'] = [event_dict['events'][0]]
        error_ticket_page = {
            "status_code": 403,
            "error_description": "Made up error",
            "error": "NOT_ALLOWED"}
        m_eventbrite.side_effect = [simple_event_dict,
                                    error_ticket_page]

        response = self.import_tickets()
        assert_alert_exists(
            response,
            'danger',
            'Error',
            eventbrite_error % (403, "Made up error"))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_inventory_event_fail(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        error_event_dict = {
            "status_code": 403,
            "error_description": "Made up error",
            "error": "NOT_ALLOWED"}
        m_eventbrite.side_effect = [error_event_dict]

        response = self.import_tickets()
        assert_alert_exists(
            response,
            'danger',
            'Error',
            eventbrite_error % (403, "Made up error"))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_get_eb_inventory_event_continuation(self, m_eventbrite):
        # privileged user gets the inventory of tickets from (fake) EB
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        simple_event_dict = copy.deepcopy(event_dict)
        simple_event_dict['pagination']['has_more_items'] = True
        simple_event_dict['pagination']['continuation'] = "eyJwYWdlIjogMn0"
        m_eventbrite.side_effect = [simple_event_dict,
                                    event_dict,
                                    ticket_dict1,
                                    ticket_dict2,
                                    ticket_dict3]
        response = self.import_tickets()
        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported %d events, %d tickets" % (3, 6)))
        assert_alert_exists(response, 'success', 'Success', (
            "BPT: imported %d tickets" % 0))

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_bpt_inventory(self, m_urlopen):
        # privileged user gets the inventory of tickets from (fake) BPT
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()

        a = Mock()
        date_filename = open("tests/ticketing/datelist.xml", 'r')
        price_filename = open("tests/ticketing/pricelist.xml", 'r')
        a.read.side_effect = [File(date_filename).read(),
                              File(price_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            no_settings_error)
        assert_alert_exists(
            response,
            'success',
            'Success',
            "BPT: imported %d tickets" % 12)
        ticket = get_object_or_404(
            TicketItem,
            ticket_id='%s-4513068' % (event.event_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.cost, Decimal('125.00'))

    def test_list_ticket_user_is_not_ticketing(self):
        # The user does not have the right privileges.
        user = ProfileFactory.create().user_object
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_list_tickets_all_good(self):
        # privileged user gets the list
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            'No ticket events have been created, use the "Create Event" ' +
            'button above to create some.')

    @patch('urllib.request.urlopen', autospec=True)
    def test_reimport_bpt_inventory(self, m_urlopen):
        # reimporting gets nothing new but doesn't fail
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        BrownPaperSettingsFactory()
        TicketItemFactory(
            ticket_id='%s-4513068' % (event.event_id),
            has_coupon=True,
            live=False,
            ticketing_event=event)
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
            ticket_id='%s-4513068' % (event.event_id))
        assert ticket.live
        assert ticket.has_coupon

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_event_detail(self, m_urlopen):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory(title='', description='')
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
            TicketingEvents,
            event_id='%s' % (event.event_id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The Great Burlesque Exposition of 2016 takes place Feb. 5-7",
            reload_event.description)

    def test_get_no_inventory(self):
        # privileged user gets the inventory of tickets with no tickets
        TicketingEvents.objects.all().delete()
        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_event_list(self, m_urlopen):
        # not event list comes when getting inventory
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory(title="", description="")
        BrownPaperSettingsFactory()

        a = Mock()
        a.read.side_effect = []
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_date_list(self, m_urlopen):
        # not date list comes when getting inventory
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory(title="", description="")
        BrownPaperSettingsFactory()

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        a.read.side_effect = [File(event_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_price_list(self, m_urlopen):
        # not price list comes when getting inventory
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory(title="", description="")
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
        # first read from BPT has a URL read error
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory(title="", description="")
        BrownPaperSettingsFactory()

        a = Mock()
        a.read.side_effect = urllib.error.URLError("test url error")
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_no_settings(self, m_urlopen):
        # not date list comes when getting inventory
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory(title="", description="")

        a = Mock()
        event_filename = open("tests/ticketing/eventlist.xml", 'r')
        a.read.side_effect = [File(event_filename).read()]
        m_urlopen.return_value = a

        response = self.import_tickets()
        self.assertEqual(response.status_code, 200)

    def test_list_tickets_for_conf(self):
        # privileged user gets the list for a conference
        t = TicketItemFactory()
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={"conference": t.ticketing_event.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Conference Classes")
        self.assertNotContains(response, "fas fa-check")

    def test_ticket_active_state(self):
        # privileged user gets the list for a conference
        at = TicketItemFactory(live=True)
        not_live_ticket = TicketItemFactory(
            live=False,
            ticketing_event=at.ticketing_event)
        coupon_ticket = TicketItemFactory(
            has_coupon=True,
            live=True,
            ticketing_event=at.ticketing_event)

        login_as(self.privileged_user, self)
        response = self.client.get(self.url, data={
            "conference": at.ticketing_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible')
        self.assertContains(response, 'Hidden')
        self.assertContains(response, 'Requires Coupon')
        self.assertContains(response, 'Regular Fee', 3)

    def test_ticket_currently_active(self):
        at = TicketItemFactory(
            live=True,
            start_time=datetime.now()-timedelta(days=1),
            end_time=datetime.now()+timedelta(days=1))

        login_as(self.privileged_user, self)
        response = self.client.get(self.url, data={
            "conference": at.ticketing_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            at.start_time.strftime('%m/%d/%Y'))
        self.assertContains(
            response,
            at.end_time.strftime('%m/%d/%Y'))
        self.assertContains(
            response,
            '<tr class="dedicated-sched gbe-table-row">')

    def test_ticket_not_yet_active(self):
        it = TicketItemFactory(
            live=True,
            start_time=datetime.now()+timedelta(days=1))

        login_as(self.privileged_user, self)
        response = self.client.get(self.url, data={
            "conference": it.ticketing_event.conference.conference_slug}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            it.start_time.strftime('%m/%d/%Y'))
        self.assertNotContains(
            response,
            '<tr class="dedicated-sched gbe-table-row">')

    def test_ticket_no_longer_active(self):
        it = TicketItemFactory(
            live=True,
            end_time=datetime.now()-timedelta(days=1))

        login_as(self.privileged_user, self)
        response = self.client.get(self.url, data={
            "conference": it.ticketing_event.conference.conference_slug}
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            it.end_time.strftime('%m/%d/%Y'))
        self.assertNotContains(
            response,
            '<tr class="dedicated-sched gbe-table-row">')

    def test_ticket_active_donation(self):
        at = TicketItemFactory(live=True, is_minimum=True)

        login_as(self.privileged_user, self)
        response = self.client.get(self.url, data={
            "conference": at.ticketing_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visible')
        self.assertContains(response, 'Minimum Donation')

    def test_ticket_includes_conference(self):
        active_ticket = TicketItemFactory(
            live=True,
            ticketing_event__include_conference=True)

        login_as(self.privileged_user, self)
        response = self.client.get(self.url)

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
        active_ticket = TicketItemFactory(
            live=True,
            ticketing_event__include_most=True)
        event = SchedEventFactory()
        EventLabelFactory(
            event=event,
            text=active_ticket.ticketing_event.conference.conference_slug)

        login_as(self.privileged_user, self)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Conference Classes")
        self.assertContains(response, event.title)
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
        event = SchedEventFactory()
        EventLabelFactory(
            event=event,
            text=active_ticket.ticketing_event.conference.conference_slug)
        active_ticket.ticketing_event.linked_events.add(event)
        active_ticket.ticketing_event.save()

        login_as(self.privileged_user, self)
        response = self.client.get(self.url)

        self.assertContains(response, "fas fa-check")
        self.assertContains(response, reverse(
            'set_ticket_to_event',
            urlconf='ticketing.urls',
            args=[active_ticket.ticketing_event.pk,
                  'TicketingEvents',
                  'off',
                  event.pk]))
        self.assertContains(response, "Remove Event from Ticket")
