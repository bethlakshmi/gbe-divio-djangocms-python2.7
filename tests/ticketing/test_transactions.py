import copy
from mock import patch, Mock
import urllib
from django.core.files import File
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ticketing.models import (
    TicketingEvents,
    EventbriteSettings,
    Purchaser,
    SyncStatus,
    Transaction
)
from tests.factories.ticketing_factories import (
    EventbriteSettingsFactory,
    PurchaserFactory,
    TicketItemFactory,
    TicketingEventsFactory,
    TransactionFactory,
)
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    get_limbo,
    grant_privilege,
    login_as,
    setup_admin_w_privs,
)
from gbetext import (
    eventbrite_error,
    import_transaction_message,
    intro_transaction_message,
    intro_trans_user_message,
    no_settings_error,
    sync_off_instructions,
)
from tests.contexts import PurchasedTicketContext
from tests.ticketing.eb_order_list import order_dict
import eventbrite


class TestTransactions(TestCase):
    '''Tests for transactions view'''

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs(['Ticketing - Transactions'])
        cls.url = reverse('transactions', urlconf='ticketing.urls')

    def setUp(self):
        self.client = Client()

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_ticket_missing(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        SyncStatus.objects.all().delete()
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
        EventbriteSettings.objects.all().delete()
        SyncStatus.objects.all().delete()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')

        limbo = get_limbo()
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
        EventbriteSettings.objects.all().delete()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')

        limbo = get_limbo()
        purchaser = PurchaserFactory(matched_to_user=limbo)
        user = UserFactory(email=purchaser.email)
        m_eventbrite.return_value = order_dict

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        test_purchaser = Purchaser.objects.get(pk=purchaser.pk)
        self.assertEqual(test_purchaser.matched_to_user, user.user_ptr)

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_change_prior_purchaser(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        limbo = get_limbo()
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')
        attendees = order_dict["attendees"][0]
        transaction = TransactionFactory(
            ticket_item=ticket,
            reference=attendees['id'],
            payment_source='Eventbrite')
        orig_purchaser = transaction.purchaser
        m_eventbrite.return_value = order_dict

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        test_purchaser = Purchaser.objects.get(
            email=attendees['profile']['email'])
        test_trans = Transaction.objects.get(
            reference=attendees['id'])
        self.assertEqual(test_trans.purchaser, test_purchaser)
        self.assertNotEqual(test_trans.purchaser, orig_purchaser)
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                1))

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_refund(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        limbo = get_limbo()
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')
        attendees = order_dict["attendees"][0]
        transaction = TransactionFactory(
            ticket_item=ticket,
            reference=attendees['id'],
            payment_source='Eventbrite')
        refund = order_dict
        refund["attendees"][0]["status"] = "Not Attending"
        m_eventbrite.return_value = refund

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})

        self.assertFalse(Transaction.objects.filter(
            reference=order_dict["attendees"][0]['id']).exists())
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                1))
        order_dict["attendees"][0]["status"] = "Attending"

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_error_status(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        limbo = get_limbo()
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')
        attendees = order_dict["attendees"][0]

        weird = order_dict
        weird["attendees"][0]["status"] = "Weird Status"
        m_eventbrite.return_value = weird

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})

        self.assertContains(
            response,
            "Unknown Status - %s, did not save it" % (
                weird["attendees"][0]["status"]))
        order_dict["attendees"][0]["status"] = "Attending"

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_pagination(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        EventbriteSettingsFactory()
        event = TicketingEventsFactory(event_id="1", source=2)
        ticket = TicketItemFactory(ticketing_event=event, ticket_id='3255985')

        limbo = get_limbo()
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
        EventbriteSettings.objects.all().delete()
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
        EventbriteSettings.objects.all().delete()
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
        EventbriteSettings.objects.all().delete()
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

    def test_user_is_not_ticketing(self):
        from ticketing.views import transactions

        # The user does not have the right privileges.  Send PermissionDenied
        user = ProfileFactory.create().user_object
        request = self.client.get(
            reverse('transactions', urlconf='ticketing.urls'),
        )
        self.assertEqual(request.status_code, 403)

    def test_transactions_w_privilege(self):
        context = PurchasedTicketContext()
        canceled_trans = TransactionFactory(
            ticket_item=context.transaction.ticket_item,
            status="canceled")
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, context.transaction.purchaser.email)
        self.assertContains(response, context.profile.display_name)
        self.assertContains(response, context.transaction.ticket_item.title, 2)
        self.assertNotContains(response, "- Vendor")
        self.assertNotContains(response, "- Act")
        self.assertContains(response, canceled_trans.purchaser.email)
        self.assertContains(response, "gbe-table-row gbe-table-danger")
        self.assertContains(response, intro_transaction_message)

    def test_transactions_w_privilege_userview_editpriv(self):
        context = PurchasedTicketContext()
        ticketing_event = context.transaction.ticket_item.ticketing_event
        ticketing_event.act_submission_event = True
        ticketing_event.save()
        old_context = PurchasedTicketContext()
        old_context.conference.status = "past"
        old_context.conference.save()
        old_context.transaction.purchaser = context.transaction.purchaser
        canceled_trans = TransactionFactory(
            ticket_item__ticketing_event__conference=context.conference,
            status="canceled")
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
            args=[context.profile.pk]))
        self.assertContains(response, intro_trans_user_message)
        self.assertContains(response, canceled_trans.ticket_item.title)
        self.assertContains(response, "gbe-table-row gbe-table-danger")
        self.assertNotContains(response,
                               old_context.transaction.ticket_item.title)

    def test_transactions_empty(self):
        TicketingEvents.objects.all().delete()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_transactions_old_conf_limbo_purchase(self):
        limbo = get_limbo()

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
        limbo = get_limbo()

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

    def test_transactions_sync_no_sources_on(self):
        TicketingEvents.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        EventbriteSettingsFactory(active_sync=False)
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            sync_off_instructions % "Eventbrite")

    def test_transactions_sync_both_on_no_events(self):
        TicketingEvents.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        EventbriteSettingsFactory()
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "%s  Transactions imported: %d -- Eventbrite" % (
                                import_transaction_message,
                                0))
