from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    make_vendor_app_purchase,
)
from gbetext import (
    bid_not_submitted_msg,
    bid_not_paid_msg,
    default_submit_msg,
)


class TestViewVendor(TestCase):
    '''Tests for view_vendor view'''
    view_name = 'vendor_view'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def test_view_vendor_all_well(self):
        vendor = VendorFactory(submitted=True)
        profile = vendor.business.owners.all().first()
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)
        self.assertContains(response, default_submit_msg)

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
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)
        self.assertNotContains(response, bid_not_submitted_msg)
        self.assertNotContains(response, bid_not_paid_msg)
        self.assertNotContains(response, default_submit_msg)

    def test_view_vendor_wrong_user(self):
        vendor = VendorFactory()
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)

        self.assertEqual(403, response.status_code)

    def test_view_vendor_not_paid(self):
        vendor = VendorFactory(submitted=False)
        profile = vendor.business.owners.all().first()
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)
        self.assertContains(response, bid_not_paid_msg)

    def test_view_vendor_not_submitted(self):
        vendor = VendorFactory(submitted=False)
        profile = vendor.business.owners.all().first()
        make_vendor_app_purchase(vendor.b_conference,
                                 profile.user_object)
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, test_string)
        self.assertContains(response, bid_not_submitted_msg)
