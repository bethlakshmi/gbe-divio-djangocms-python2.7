import copy
from mock import patch, Mock
import urllib
from django.core.files import File
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ticketing.models import (
    TicketingEvents,
    BrownPaperSettings,
    EventbriteSettings,
    Purchaser,
    SyncStatus,
    Transaction
)
from tests.factories.ticketing_factories import (
    BrownPaperSettingsFactory,
    EventbriteSettingsFactory,
    PurchaserFactory,
    TicketItemFactory,
    TicketingEventsFactory,
)
import nose.tools as nt
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import (
    transactions
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from gbetext import (
    eventbrite_error,
    import_transaction_message,
    no_settings_error,
    sync_off_instructions,
)
from tests.contexts import PurchasedTicketContext
from tests.ticketing.eb_order_list import order_dict
import eventbrite


class TestTransactions(TestCase):
    '''Tests for transactions view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory()
        grant_privilege(self.privileged_user, 'Ticketing - Transactions')
        self.url = reverse('transactions', urlconf='ticketing.urls')

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_ticket_missing(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        SyncStatus.objects.all().delete()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)

        m_eventbrite.return_value = order_dict

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'danger',
                            'Error',
                            "Ticket Item for id 3255985 does not exist")
        error_status = SyncStatus.objects.filter(is_success=False).first()
        success_status = SyncStatus.objects.filter(is_success=True).first()
        self.assertEqual(error_status.error_msg,
                         "Ticket Item for id 3255985 does not exist")
        self.assertEqual(success_status.import_type,
                         "EB Transaction")
        self.assertEqual(success_status.import_number,
                         0)

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_only(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        SyncStatus.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')

        limbo, created = User.objects.get_or_create(username='limbo')
        m_eventbrite.return_value = order_dict

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                1))
        success_status = SyncStatus.objects.filter(is_success=True).first()
        self.assertEqual(success_status.import_type,
                         "EB Transaction")
        self.assertEqual(success_status.import_number,
                         1)

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_match_prior_purchaser(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')

        limbo, created = User.objects.get_or_create(username='limbo')
        purchaser = PurchaserFactory(matched_to_user=limbo)
        user = UserFactory(email=purchaser.email)
        m_eventbrite.return_value = order_dict

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        test_purchaser = Purchaser.objects.get(pk=purchaser.pk)
        self.assertEqual(test_purchaser.matched_to_user, user)

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_pagination(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')

        limbo, created = User.objects.get_or_create(username='limbo')
        continue_order_page = copy.deepcopy(order_dict)
        continue_order_page['pagination']['has_more_items'] = True
        continue_order_page['pagination']['continuation'] = "eyJwYWdlIjogMn0"
        m_eventbrite.side_effect = [continue_order_page,
                                    order_dict]

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                1))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_w_purchaser(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')
        purchaser = PurchaserFactory()
        known_buyer_order = order_dict
        known_buyer_order['attendees'][0]["profile"]["email"] = purchaser.email
        m_eventbrite.return_value = known_buyer_order

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                1))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_w_user(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')
        profile = ProfileFactory()
        known_buyer_order = order_dict
        known_buyer_order[
            'attendees'][0]["profile"]["email"] = profile.purchase_email
        m_eventbrite.return_value = known_buyer_order

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                1))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_bad_auth_token(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')

        m_eventbrite.side_effect = [{
            "status_code": 401,
            "error_description": "The OAuth token you provided was invalid.",
            "error": "NOT_AUTH"}]

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response, 'danger', 'Error', eventbrite_error % (
            401,
            "The OAuth token you provided was invalid."))

    @nt.raises(PermissionDenied)
    def test_user_is_not_ticketing(self):
        # The user does not have the right privileges.  Send PermissionDenied
        user = ProfileFactory.create().user_object
        request = self.factory.get(
            reverse('transactions', urlconf='ticketing.urls'),
        )
        request.user = user
        response = transactions(request)

    def test_transactions_w_privilege(self):
        context = PurchasedTicketContext()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, context.transaction.purchaser.email)
        self.assertContains(response, context.profile.display_name)
        self.assertContains(response, context.transaction.ticket_item.title)
        self.assertNotContains(response, "- Vendor")
        self.assertNotContains(response, "- Act")

    def test_transactions_w_privilege_userview_editpriv(self):
        context = PurchasedTicketContext()
        context.transaction.ticket_item.ticketing_event.act_submission_event = True
        context.transaction.ticket_item.ticketing_event.save()
        grant_privilege(self.privileged_user, 'Registrar')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url + "?format=user")
        self.assertContains(response, context.profile.user_object.email)
        self.assertContains(response, context.profile.display_name)
        self.assertContains(response,
                            "%s - Act" % context.transaction.ticket_item.title)
        self.assertNotContains(response, "- Vendor")
        self.assertContains(response, reverse(
            'admin_profile',
            urlconf="gbe.urls",
            args=[context.profile.resourceitem_id]))

    def test_transactions_empty(self):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        nt.assert_equal(response.status_code, 200)

    def test_transactions_old_conf_limbo_purchase(self):
        limbo, created = User.objects.get_or_create(username='limbo')
        old_context = PurchasedTicketContext()
        old_context.conference.status = "past"
        old_context.conference.save()
        old_context.transaction.purchaser.matched_to_user = limbo
        old_context.transaction.purchaser.save()
        old_ticket = old_context.transaction.ticket_item
        old_ticket.ticketing_event.vendor_submission_event = True
        old_ticket.ticketing_event.save()
        context = PurchasedTicketContext()
        login_as(self.privileged_user, self)
        response = self.client.get("%s?conference=%s" % (
            self.url,
            old_context.conference.conference_slug))
        self.assertContains(response, old_context.transaction.purchaser.email)
        self.assertContains(response, "%s, %s" % (
            old_context.transaction.purchaser.last_name,
            old_context.transaction.purchaser.first_name))
        self.assertContains(
            response,
            "%s - Vendor" % old_context.transaction.ticket_item.title)
        self.assertNotContains(response, "- Act")
        self.assertNotContains(response, context.transaction.purchaser.email)
        self.assertNotContains(response,
                               context.profile.user_object.first_name)
        self.assertNotContains(response, context.transaction.ticket_item.title)

    def test_transactions_old_conf_limbo_purchase_user_view(self):
        limbo, created = User.objects.get_or_create(username='limbo')
        old_context = PurchasedTicketContext()
        old_context.conference.status = "past"
        old_context.conference.save()
        old_context.transaction.purchaser.matched_to_user = limbo
        old_context.transaction.purchaser.save()
        context = PurchasedTicketContext()
        login_as(self.privileged_user, self)
        response = self.client.get("%s?format=user&conference=%s" % (
            self.url,
            old_context.conference.conference_slug))
        self.assertContains(response, old_context.transaction.purchaser.email)
        self.assertContains(response, "N/A<br>(%s, %s)" % (
            old_context.transaction.purchaser.last_name,
            old_context.transaction.purchaser.first_name))
        self.assertContains(response,
                            old_context.transaction.ticket_item.title)
        self.assertNotContains(response, "- Vendor")
        self.assertNotContains(response, "- Act")
        self.assertNotContains(response, context.transaction.purchaser.email)
        self.assertNotContains(response,
                               context.profile.user_object.first_name)
        self.assertNotContains(response, context.transaction.ticket_item.title)

    @patch('urllib.request.urlopen', autospec=True)
    def test_transactions_sync_bpt_only(self, m_urlopen):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        BrownPaperSettingsFactory()
        event = TicketingEventsFactory(event_id="1")
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))

        limbo, created = User.objects.get_or_create(username='limbo')

        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        nt.assert_equal(response.status_code, 200)

        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        nt.assert_equal(str(transaction.order_date),
                        "2014-08-15 19:26:56")
        nt.assert_equal(transaction.shipping_method, 'Will Call')
        nt.assert_equal(transaction.order_notes, 'None')
        nt.assert_equal(transaction.payment_source, 'Brown Paper Tickets')
        nt.assert_equal(transaction.purchaser.email, 'test@tickets.com')
        nt.assert_equal(transaction.purchaser.phone, '111-222-3333')
        nt.assert_equal(transaction.purchaser.matched_to_user, limbo)
        nt.assert_equal(transaction.purchaser.first_name, 'John')
        nt.assert_equal(transaction.purchaser.last_name, 'Smith')
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s   Transactions imported: %s - BPT" % (
                                import_transaction_message,
                                "1"))
        assert_alert_exists(response, 'danger', 'Error', no_settings_error)

    def test_transactions_sync_no_sources_on(self):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
        EventbriteSettingsFactory(active_sync=False)
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s   Transactions imported: %s - BPT" % (
                                import_transaction_message,
                                "0"))
        assert_alert_exists(response,
                            'success',
                            'Success',
                            sync_off_instructions % "Eventbrite")

    def test_transactions_sync_both_on_no_events(self):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
        EventbriteSettingsFactory()
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s   Transactions imported: %s - BPT" % (
                                import_transaction_message,
                                "0"))
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                0))
