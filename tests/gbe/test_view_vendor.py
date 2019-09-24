import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestViewVendor(TestCase):
    '''Tests for view_vendor view'''
    view_name = 'vendor_view'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def test_view_vendor_all_well(self):
        vendor = VendorFactory(submitted=True)
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(vendor.profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)

    def test_view_vendor_privileged_user(self):
        vendor = VendorFactory(submitted=True)
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')

        staff_user = ProfileFactory()
        grant_privilege(staff_user, "Vendor Reviewers")
        login_as(staff_user, self)

        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)

    def test_view_vendor_wrong_user(self):
        vendor = VendorFactory()
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)

        nt.assert_equal(403, response.status_code)
