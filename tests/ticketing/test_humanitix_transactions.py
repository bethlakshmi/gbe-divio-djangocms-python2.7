from django.test import TestCase
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
    BrownPaperSettings,
    HumanitixSettings,
    Purchaser,
    SyncStatus,
    Transaction
)
from tests.factories.ticketing_factories import (
    BrownPaperSettingsFactory,
    HumanitixSettingsFactory,
    PurchaserFactory,
    TicketPackageFactory,
    TicketTypeFactory,
    TicketingEventsFactory,
    TransactionFactory,
)
from django.contrib.auth.models import User
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
    no_ht_settings_error,
    sync_off_instructions,
)
from tests.contexts import PurchasedTicketContext
from tests.ticketing.mock_ht_response import MockHTResponse
from tests.ticketing.ht_transactions import (
    order_list,
    complete_trans,
    canceled_trans,
)


class TestHumanitixTransactions(TestCase):
    '''Tests for humanitix sync in transactions view'''

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs(['Ticketing - Transactions'])
        cls.url = reverse('transactions', urlconf='ticketing.urls')
        BrownPaperSettingsFactory(active_sync=False)
        EventbriteSettings.objects.all().delete()

    def setUp(self):
        TicketingEvents.objects.all().delete()
        Purchaser.objects.all().delete()
        SyncStatus.objects.all().delete()

    @patch('requests.get', autospec=True)
    def test_transactions_sync_missing_package_cancel_none(self, m_humanitix):
        HumanitixSettingsFactory()
        ticket1 = TicketTypeFactory(ticketing_event__source=3,
                                    ticket_id="656b90657cf8549dd8238a10")
        ticket2 = TicketTypeFactory(ticketing_event=ticket1.ticketing_event,
                                    ticket_id="6568c4ee7cf8549dd8238a0c")
        limbo = get_limbo()
        m_humanitix.side_effect = [MockHTResponse(json_data=order_list),
                                   MockHTResponse(json_data=complete_trans),
                                   MockHTResponse(json_data=canceled_trans)]

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "Imported 0 packages and 3 tickets")
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "Canceled 0 transactions")
        success_status = SyncStatus.objects.filter(
            is_success=True,
            import_type="HT Transaction").first()
        self.assertEqual(success_status.import_number, 3)
        cancel_status = SyncStatus.objects.filter(
            is_success=True,
            import_type="HT Cancellations").first()
        self.assertEqual(cancel_status.import_number, 0)

    @patch('requests.get', autospec=True)
    def test_transactions_sync_missing_ticket_w_known_buyer(self, m_humanitix):
        HumanitixSettingsFactory()
        package = TicketPackageFactory(ticketing_event__source=3,
                                       ticket_id="6568c6ca6e0f8730e1bd5f1a")
        ticket1 = TicketTypeFactory(ticketing_event=package.ticketing_event,
                                    ticket_id="6568c4ee7cf8549dd8238a0c")
        limbo = get_limbo()
        purchaser = PurchaserFactory(
            matched_to_user__email="testuser@gmail.com",
            email="testuser@gmail.com")


        m_humanitix.side_effect = [MockHTResponse(json_data=order_list),
                                   MockHTResponse(json_data=complete_trans),
                                   MockHTResponse(json_data=canceled_trans)]

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "Imported 3 packages and 2 tickets")
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "Canceled 1 transactions")
        success_status = SyncStatus.objects.filter(
            is_success=True,
            import_type="HT Transaction").first()
        self.assertEqual(success_status.import_number, 5)
        cancel_status = SyncStatus.objects.filter(
            is_success=True,
            import_type="HT Cancellations").first()
        self.assertEqual(cancel_status.import_number, 1)
        self.assertTrue(Transaction.objects.filter(
            purchaser=purchaser,
            reference="659880a26ec9d043e436d03c").exists())

    def test_humanitix_settings_missing(self):
        HumanitixSettings.objects.all().delete()
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'danger',
                            'Error',
                            no_ht_settings_error)

    @patch('requests.get', autospec=True)
    def test_bad_api_key_orders(self, m_humanitix):
        HumanitixSettingsFactory()
        package = TicketPackageFactory(ticketing_event__source=3,
                                       ticket_id="6568c6ca6e0f8730e1bd5f1a")
        m_humanitix.side_effect = [MockHTResponse(
            json_data={'error': "Bad Request",
                       'message': "Invalid api key format provided."},
            status_code=400)]
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(
            response,
            'danger',
            'Error',
            'Bad Request - Invalid api key format provided.')

    @patch('requests.get', autospec=True)
    def test_bad_api_key_completed_trans(self, m_humanitix):
        HumanitixSettingsFactory()
        package = TicketPackageFactory(ticketing_event__source=3,
                                       ticket_id="6568c6ca6e0f8730e1bd5f1a")
        m_humanitix.side_effect = [
            MockHTResponse(json_data=order_list),
            MockHTResponse(
                json_data={'error': "Bad Request",
                           'message': "Error on completed ticket request."},
                status_code=400),
            MockHTResponse(json_data=canceled_trans)]
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(
            response,
            'danger',
            'Error',
            'Bad Request - Error on completed ticket request.')

    @patch('requests.get', autospec=True)
    def test_bad_api_key_canceled_trans(self, m_humanitix):
        HumanitixSettingsFactory()
        package = TicketPackageFactory(ticketing_event__source=3,
                                       ticket_id="6568c6ca6e0f8730e1bd5f1a")
        limbo = get_limbo()
        m_humanitix.side_effect = [
            MockHTResponse(json_data=order_list),
            MockHTResponse(json_data=complete_trans),
            MockHTResponse(
                json_data={'error': "Bad Request",
                           'message': "Error on cancelled ticket request."},
                status_code=400)]
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(
            response,
            'danger',
            'Error',
            'Bad Request - Error on cancelled ticket request.')

    @patch('requests.get', autospec=True)
    def test_transactions_sync_multi_pages(self, m_humanitix):
        HumanitixSettingsFactory()
        package = TicketPackageFactory(ticketing_event__source=3,
                                       ticket_id="6568c6ca6e0f8730e1bd5f1a")
        ticket1 = TicketTypeFactory(ticketing_event=package.ticketing_event,
                                    ticket_id="656b90657cf8549dd8238a10")
        ticket2 = TicketTypeFactory(ticketing_event=package.ticketing_event,
                                    ticket_id="6568c4ee7cf8549dd8238a0c")
        limbo = get_limbo()
        short_order_listm = copy.deepcopy(order_list)
        short_order_listm['pageSize'] = 2
        short_compl_trans = copy.deepcopy(complete_trans)
        short_compl_trans['pageSize'] = 2
        short_canceled_trans = copy.deepcopy(canceled_trans)
        short_canceled_trans['pageSize'] = 2
        m_humanitix.side_effect = [
            MockHTResponse(json_data=short_order_listm),
            MockHTResponse(json_data={"total": 2,
                                      "pageSize": 2,
                                      "page": 2,
                                      "orders": []}),
            MockHTResponse(json_data=short_compl_trans),
            MockHTResponse(json_data={"total": 2,
                                      "pageSize": 2,
                                      "page": 2,
                                      "tickets": []}),
            MockHTResponse(json_data=short_canceled_trans),
            MockHTResponse(json_data={"total": 2,
                                      "pageSize": 2,
                                      "page": 2,
                                      "tickets": []})]

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={'Sync': 'Sync'})
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "Imported 3 packages and 3 tickets")
        assert_alert_exists(response,
                            'success',
                            'Success',
                            "Canceled 1 transactions")
        success_status = SyncStatus.objects.filter(
            is_success=True,
            import_type="HT Transaction").first()
        self.assertEqual(success_status.import_number, 6)
        cancel_status = SyncStatus.objects.filter(
            is_success=True,
            import_type="HT Cancellations").first()
        self.assertEqual(cancel_status.import_number, 1)

'''

    @patch('eventbrite.Eventbrite.get', autospec=True)
    def test_transactions_sync_eb_match_prior_purchaser(self, m_eventbrite):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
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
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
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
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
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
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory(active_sync=False)
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
        BrownPaperSettings.objects.all().delete()
        EventbriteSettings.objects.all().delete()
        BrownPaperSettingsFactory()
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

    def test_user_is_not_ticketing(self):
        from ticketing.views import transactions

        # The user does not have the right privileges.  Send PermissionDenied
        user = ProfileFactory.create().user_object
        request = self.client.get(
            reverse('transactions', urlconf='ticketing.urls'),
        )
        request.user = user
        with self.assertRaises(PermissionDenied):
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
        ticketing_event = context.transaction.ticket_item.ticketing_event
        ticketing_event.act_submission_event = True
        ticketing_event.save()
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

    def test_transactions_empty(self):
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
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
'''
