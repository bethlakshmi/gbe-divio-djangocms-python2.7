import copy
from django.test import TestCase
from django.test.utils import override_settings
from mock import patch, Mock
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.urls import reverse
from ticketing.models import (
    TicketingEvents,
    BrownPaperSettings,
    HumanitixSettings,
    TicketPackage,
    TicketType,
)
from tests.factories.ticketing_factories import (
    BrownPaperSettingsFactory,
    HumanitixSettingsFactory,
    TicketPackageFactory,
    TicketTypeFactory,
    TicketingEventsFactory,
)
from tests.factories.gbe_factories import ProfileFactory
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    SchedEventFactory,
)
from gbetext import (
    no_ht_settings_error,
    sync_off_instructions,
)
from tests.ticketing.ht_event_list import get_events
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)


class MockHTResponse:
    def __init__(self,
                 json_data=None,
                 status_code=200):
        if json_data is not None:
            self.json_data = json_data
        self.status_code = status_code

    # mock json() method always returns a specific testing dictionary
    def json(self):
        return self.json_data


class TestGetHumanitixTickets(TestCase):
    '''Tests for fetching event/ticket data from Humanitix (HT)'''
    view_name = 'ticket_items'

    def setUp(self):
        TicketingEvents.objects.all().delete()

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory.create().user_object
        grant_privilege(cls.privileged_user, 'Ticketing - Admin')
        cls.url = reverse(cls.view_name, urlconf='ticketing.urls')
        BrownPaperSettingsFactory(active_sync=False)

    def import_tickets(self):
        data = {'Import': 'Import'}
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data)
        return response

    @override_settings(DEBUG=True)
    @patch('requests.get', autospec=True)
    def test_get_debug_server_w_organiser(self, m_humanitix):
        HumanitixSettingsFactory(system=0)
        m_humanitix.side_effect = [MockHTResponse(json_data=get_events)]

        response = self.import_tickets()
        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported 1 events, 11 tickets, 3 packages"))
        self.assertFalse(TicketPackage.objects.filter(
            ticket_id='6568c6ca6e0f8730e1bd5f1d').exists())
        ticket = get_object_or_404(TicketType,
                                   ticket_id='650e0b1b00c168315ead7e0c')
        self.assertEqual(ticket.cost, Decimal('45.00'))
        self.assertTrue(TicketType.objects.get(
            ticket_id="6581f5ab7e2ccc7b22e27e18").is_minimum)

    def test_humanitix_settings_missing(self):
        HumanitixSettings.objects.all().delete()
        login_as(self.privileged_user, self)
        response = self.import_tickets()
        assert_alert_exists(response,
                            'danger',
                            'Error',
                            no_ht_settings_error)

    def test_humanitix_sync_off(self):
        HumanitixSettingsFactory(active_sync=False)
        login_as(self.privileged_user, self)
        response = self.import_tickets()
        assert_alert_exists(response,
                            'success',
                            'Success',
                            sync_off_instructions % "Humanitix")

    @patch('requests.get', autospec=True)
    def test_bad_api_key(self, m_humanitix):
        HumanitixSettingsFactory(organiser_id=None)
        m_humanitix.side_effect = [MockHTResponse(
            json_data={'error': "Bad Request",
                       'message': "Invalid api key format provided."},
            status_code=400)]

        response = self.import_tickets()
        assert_alert_exists(
            response,
            'danger',
            'Error',
            'Bad Request - Invalid api key format provided.')

    @patch('requests.get', autospec=True)
    def test_get_w_pagination_package_exists(self, m_humanitix):
        # event & package does not get reimported, new tickets/packages get.
        # chained to event. This pagination is a bit of a fake, since we
        # only ever have 1 event I have no way to live test this.
        HumanitixSettingsFactory()
        event = TicketingEventsFactory(event_id="6500d67ba66ab3cb5aae377c",
                                       source=3)
        package = TicketPackageFactory(
            ticket_id="650e0c68949d9cc723ed3330",
            ticketing_event=event,
            cost=10.00)

        small_size = copy.deepcopy(get_events)
        small_size['pageSize'] = 2
        m_humanitix.side_effect = [MockHTResponse(json_data=small_size),
                                   MockHTResponse(json_data={"total": 2,
                                                             "pageSize": 2,
                                                             "page": 2,
                                                             "events": []})]

        response = self.import_tickets()
        refresh_package = get_object_or_404(TicketPackage, pk=package.pk)

        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported 0 events, 11 tickets, 2 packages"))
        self.assertTrue(TicketType.objects.filter(
            ticket_id='650e0b1b00c168315ead7e0c',
            ticketing_event=event).exists())
        self.assertEqual(refresh_package.cost, Decimal('20.00'))
        self.assertTrue(TicketPackage.objects.filter(
            ticket_id='65820750ea22e8338a0fae2b',
            ticketing_event=event).exists())

    @patch('requests.get', autospec=True)
    def test_get_w_ticket_exists_no_org(self, m_humanitix):
        # event & ticket does not get reimported but cost is changed.
        # uses Price Range to test min cost.
        HumanitixSettingsFactory(organiser_id=None)
        event = TicketingEventsFactory(event_id="6568c47844bea90207cb25af",
                                       source=3)
        ticket = TicketTypeFactory(
            ticket_id="656b90657cf8549dd8238a10",
            has_coupon=True,
            live=False,
            ticketing_event=event,
            cost=10.00,
            is_minimum=False)

        m_humanitix.side_effect = [MockHTResponse(json_data=get_events)]

        response = self.import_tickets()
        refresh_ticket = get_object_or_404(TicketType, pk=ticket.pk)
        self.assertEqual(refresh_ticket.cost, Decimal('5.00'))
        ticket = get_object_or_404(TicketPackage,
                                   ticket_id='650e0c68949d9cc723ed3330')
        self.assertEqual(ticket.cost, Decimal('20.00'))
        ticket = get_object_or_404(TicketType,
                                   ticket_id='6568c4ee7cf8549dd8238a0c')
        self.assertEqual(ticket.cost, Decimal('200.50'))
        self.assertEqual(refresh_ticket.is_minimum, True)
        self.assertEqual(refresh_ticket.has_coupon, True)
        self.assertEqual(refresh_ticket.live, False)
        assert_alert_exists(response, 'success', 'Success', (
            "Successfully imported 1 events, 16 tickets, 5 packages"))

    def test_package_includes_conference(self):
        package = TicketPackageFactory(
            live=True,
            conference_only_pass=True,
            ticketing_event__source=3)
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, data={
            "conference": package.ticketing_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Conference: True")
        self.assertContains(response, "fas fa-check")
        self.assertNotContains(response, "set_ticket_to_event")
        self.assertContains(
            response,
            "To change, edit package and remove 'Whole Shebang' or " +
            "'Conference Only Pass'")

    def test_package_includes_whole_shebang(self):
        package = TicketPackageFactory(
            live=True,
            whole_shebang=True,
            ticketing_event__source=3)
        event = SchedEventFactory()
        EventLabelFactory(
            event=event,
            text=package.ticketing_event.conference.conference_slug)
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, data={
            "conference": package.ticketing_event.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Whole Shebang: True")
        self.assertContains(response, event.title)
        self.assertContains(response, "fas fa-check", 2)
        self.assertNotContains(response, "set_ticket_to_event")
        self.assertContains(
            response,
            "To change, edit package and remove 'Whole Shebang' or " +
            "'Conference Only Pass'")
        self.assertContains(
            response,
            "To change, edit package and remove 'Whole Shebang'")

    def test_tickettype_linked_event(self):
        active_ticket = TicketTypeFactory(live=True, ticketing_event__source=3)
        event = SchedEventFactory()
        EventLabelFactory(
            event=event,
            text=active_ticket.ticketing_event.conference.conference_slug)
        active_ticket.linked_events.add(event)
        active_ticket.save()
        url = reverse(
            self.view_name,
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertContains(response, "fas fa-check")
        self.assertContains(response, reverse(
            'set_ticket_to_event',
            urlconf='ticketing.urls',
            args=[active_ticket.pk, 'TicketType', 'off', event.pk]))
        self.assertContains(response, "Remove Event from Ticket")
