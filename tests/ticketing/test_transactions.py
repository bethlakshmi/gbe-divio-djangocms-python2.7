from django.http import Http404
from django.core.files import File
from django.core.exceptions import PermissionDenied
from ticketing.models import (
    BrownPaperEvents,
    BrownPaperSettings,
    Transaction
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    BrownPaperSettingsFactory,
    TicketItemFactory
)
import nose.tools as nt
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import (
    transactions
)
from tests.factories.gbe_factories import (
    ProfileFactory
)
from mock import patch, Mock
import urllib2
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from tests.functions.gbe_functions import login_as


class TestTransactions(TestCase):
    '''Tests for transactions view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        group, created = Group.objects.get_or_create(
            name='Ticketing - Transactions')
        self.privileged_user = ProfileFactory.create().\
            user_object
        self.privileged_user.groups.add(group)
        self.url = reverse('transactions', urlconf='ticketing.urls')

    @nt.raises(PermissionDenied)
    def test_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = ProfileFactory.create().user_object
        request = self.factory.get(
            reverse('transactions', urlconf='ticketing.urls'),
        )
        request.user = user
        response = transactions(request)

    def test_transactions_w_privilege(self):
        '''
           privileged user gets the list
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        event = BrownPaperEventsFactory()
        ticket = TicketItemFactory(
            bpt_event=event,
            ticket_id='%s-%s' % (event.bpt_event_id, '3255985'))
        BrownPaperSettingsFactory()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        nt.assert_equal(response.status_code, 200)

    def test_transactions_empty(self):
        '''
           privileged user gets the list
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        nt.assert_equal(response.status_code, 200)

    @patch('urllib2.urlopen', autospec=True)
    def test_transactions_sync(self, m_urlopen):
        '''
           privileged user syncs orders
        '''
        BrownPaperEvents.objects.all().delete()
        BrownPaperSettings.objects.all().delete()
        BrownPaperSettingsFactory()
        event = BrownPaperEventsFactory(bpt_event_id="1")
        ticket = TicketItemFactory(
            bpt_event=event,
            ticket_id='%s-%s' % (event.bpt_event_id, '3255985'))

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
                        "2014-08-16 00:26:56+00:00")
        nt.assert_equal(transaction.shipping_method, 'Will Call')
        nt.assert_equal(transaction.order_notes, 'None')
        nt.assert_equal(transaction.payment_source, 'Brown Paper Tickets')
        nt.assert_equal(transaction.purchaser.email, 'test@tickets.com')
        nt.assert_equal(transaction.purchaser.phone, '111-222-3333')
        nt.assert_equal(transaction.purchaser.matched_to_user, limbo)
        nt.assert_equal(transaction.purchaser.first_name, 'John')
        nt.assert_equal(transaction.purchaser.last_name, 'Smith')
