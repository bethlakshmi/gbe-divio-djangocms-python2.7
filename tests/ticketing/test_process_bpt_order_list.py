from django.core.files import File
from ticketing.models import (
    TicketingEvents,
    BrownPaperSettings,
    TicketItem,
    Transaction
)
from tests.factories.ticketing_factories import (
    TicketingEventsFactory,
    BrownPaperSettingsFactory,
    TicketItemFactory
)
from django.test import TestCase
from ticketing.brown_paper import process_bpt_order_list
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory
)
from mock import patch, Mock
import urllib
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from tests.functions.gbe_functions import get_limbo


class TestProcessBPTOrderList(TestCase):
    '''Tests processing BPT Order list (the cron job)'''

    def test_get_no_events(self):
        '''
           no events are available to process
        '''
        TicketingEvents.objects.all().delete()

        self.assertEqual(process_bpt_order_list(), 0)

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_limbo(self, m_urlopen):
        '''
           get a transaction for the limbo user
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        limbo = get_limbo()

        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user, limbo.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_purchase_email(self, m_urlopen):
        '''
           get a transaction for a real user via the purchase_email
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        profile = ProfileFactory(purchase_email='test@tickets.com')

        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user,
                         profile.user_object.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')
        profile.user_object.delete()

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_purchase_email_case_mismatch(self, m_urlopen):
        '''
           get a transaction for a real user via the purchase_email
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        profile = ProfileFactory(purchase_email='Test@Tickets.com')

        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user,
                         profile.user_object.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')
        profile.user_object.delete()

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_user_by_id(self, m_urlopen):
        '''
           get a transaction for a real user with transaction id match
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        profile = ProfileFactory(purchase_email='test@tickets.com')

        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')

        a.read.side_effect = [
            File(order_filename).read().replace(
                'tracker12345',
                'ID-'+str(profile.user_object.pk))]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user,
                         profile.user_object.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')
        profile.user_object.delete()

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_fake_out(self, m_urlopen):
        '''
           in a case of user email vs. purchase email, purchase wins.
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        limbo = get_limbo()

        user = UserFactory(email='test@tickets.com')
        profile = ProfileFactory(user_object=user,
                                 purchase_email='nomatch@tickets.com')
        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user, limbo.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')
        user.delete()

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_profile(self, m_urlopen):
        '''
           match to a user with no purchase_email, but matching email
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        user = UserFactory(email='test@tickets.com')
        profile = ProfileFactory(user_object=user,
                                 purchase_email='')
        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user, user.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')
        user.delete()

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_user(self, m_urlopen):
        '''
           match to a user with no purchase_email, but matching email
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        user = UserFactory(email='test@tickets.com')
        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user, user.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')
        user.delete()

    @patch('urllib.request.urlopen', autospec=True)
    def test_get_transaction_user_case_mismatch(self, m_urlopen):
        '''
           match to a user with no purchase_email, but matching email
        '''
        TicketingEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = TicketingEventsFactory()
        ticket = TicketItemFactory(
            ticketing_event=event,
            ticket_id='%s-%s' % (event.event_id, '3255985'))
        BrownPaperSettingsFactory()
        user = UserFactory(email='Test@Tickets.com')
        a = Mock()
        order_filename = open("tests/ticketing/orderlist.xml", 'r')
        a.read.side_effect = [File(order_filename).read()]
        m_urlopen.return_value = a

        self.assertEqual(process_bpt_order_list(), 1)
        transaction = get_object_or_404(
            Transaction,
            reference='A12345678')
        self.assertEqual(str(transaction.order_date), "2014-08-15 19:26:56")
        self.assertEqual(transaction.shipping_method, 'Will Call')
        self.assertEqual(transaction.order_notes, 'None')
        self.assertEqual(transaction.payment_source, 'Brown Paper Tickets')
        self.assertEqual(transaction.purchaser.email, 'test@tickets.com')
        self.assertEqual(transaction.purchaser.phone, '111-222-3333')
        self.assertEqual(transaction.purchaser.matched_to_user, user.user_ptr)
        self.assertEqual(transaction.purchaser.first_name, 'John')
        self.assertEqual(transaction.purchaser.last_name, 'Smith')
        user.delete()
