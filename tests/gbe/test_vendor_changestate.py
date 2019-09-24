import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    VendorFactory,
    ProfileFactory
)
from django.core.exceptions import PermissionDenied
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestVendorChangestate(TestCase):
    '''Tests for vendor_changestate view'''
    view_name = 'vendor_changestate'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.vendor = VendorFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Vendor Coordinator')
        self.data = {'accepted': '3'}

    def test_vendor_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        nt.assert_equal(response.status_code, 302)

    def test_vendor_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        url = reverse(self.view_name,
                      args=[self.vendor.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url, data=self.data)
        nt.assert_equal(response.status_code, 403)
