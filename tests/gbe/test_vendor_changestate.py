from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    VendorFactory,
    ProfileFactory
)
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
        self.vendor = VendorFactory(submitted=True)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Vendor Coordinator')
        grant_privilege(self.privileged_user, 'Vendor Reviewers')
        self.data = {'accepted': '3',
                     'level': 'Featured'}

    def test_vendor_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data, follow=True)
        self.assertRedirects(response, reverse(
            "vendor_review_list",
            urlconf='gbe.urls'))
        self.assertContains(response, ", Featured")

    def test_vendor_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        url = reverse(self.view_name,
                      args=[self.vendor.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url, data=self.data)
        self.assertEqual(response.status_code, 403)
