import gbe.models as conf
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    VendorFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    )
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
)

from django.core.exceptions import PermissionDenied


class TestReviewVendorList(TestCase):
    '''Tests for review_vendor_list view'''
    view_name = 'vendor_review_list'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Vendor Reviewers')
        self.conference = current_conference()
        self.vendors = VendorFactory.create_batch(
            4,
            b_conference=self.conference,
            submitted=True)

    def test_review_vendor_all_well(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, 'Bid Information')

    def test_review_vendor_bad_user(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(403, response.status_code)

    def test_review_vendor_no_profile(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(403, response.status_code)

    def test_review_vendor_with_conf_slug(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})

        nt.assert_equal(200, response.status_code)
        for vendor in self.vendors:
            self.assertContains(response, vendor.business.name)

    def test_review_vendor_inactive_user(self):
        inactive_profile = ProfileFactory(user_object__is_active=False)
        self.vendors = VendorFactory(
            business__owners=[inactive_profile],
            b_conference=self.conference,
            submitted=True)
        url = reverse('vendor_review', urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertContains(response, 'gbe-table-row gbe-table-danger')
