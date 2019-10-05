from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    bad_id_for,
    grant_privilege,
    is_login_page,
    login_as,
)
from gbe.models import Vendor


class TestReviewVendor(TestCase):
    '''Tests for review_vendor view'''
    view_name = 'vendor_review'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Vendor Reviewers')
        self.coordinator = ProfileFactory()
        grant_privilege(self.coordinator.user_object, 'Vendor Reviewers')
        grant_privilege(self.coordinator.user_object, 'Vendor Coordinator')

    def test_review_vendor_all_well(self):
        vendor = VendorFactory()
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_review_vendor_past_conference(self):
        conference = ConferenceFactory(status='completed')
        vendor = VendorFactory(b_conference=conference)
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('vendor_view', urlconf='gbe.urls', args=[vendor.pk]))
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Review Information' in response.content)

    def test_review_vendor_post_valid_form(self):
        vendor = VendorFactory(accepted=1)
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.coordinator, self)
        data = {'vote': 3,
                'notes': "notes",
                'bid': vendor.pk,
                'evaluator': self.privileged_profile.pk}

        response = self.client.post(url, data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue("Bid Information" in response.content)

    def test_review_vendor_post_invalid_form(self):
        vendor = VendorFactory(accepted=1)
        original_state = vendor.accepted
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.coordinator, self)
        data = {'vote': 3,
                'notes': "notes",
                'bid': "forty-two",
                'evaluator': self.privileged_profile.pk}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue("Bid Information" in response.content)

    def test_review_vendor_all_well_vendor_coordinator(self):
        vendor = VendorFactory()
        login_as(self.coordinator, self)
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_coordinator_sees_control(self):
        vendor = VendorFactory()
        login_as(self.coordinator, self)
        url = reverse(self.view_name,
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        assert "<h2>Bid Control for Coordinator</h2>" in response.content

    def test_no_login_gives_error(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_vendor_id(self):
        login_as(ProfileFactory(), self)
        bad_id = bad_id_for(Vendor)
        url = reverse(self.view_name, args=[bad_id], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
