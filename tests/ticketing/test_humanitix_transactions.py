from django.test import TestCase
import copy
from mock import patch, Mock
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
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    get_limbo,
    login_as,
    setup_admin_w_privs,
)
from gbetext import no_ht_settings_error
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
