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


class TestReviewVendorList(TestCase):
    '''Tests for review_vendor_list view'''
    view_name = 'vendor_review_list'

    @classmethod
    def setUpTestData(cls):
        cls.performer = PersonaFactory()
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Vendor Reviewers')
        cls.conference = current_conference()
        cls.vendors = VendorFactory.create_batch(
            4,
            b_conference=cls.conference,
            submitted=True)

    def setUp(self):
        self.client = Client()

    def test_review_vendor_all_well(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vendor Proposals')

    def test_review_vendor_bad_user(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_review_vendor_no_profile(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_review_vendor_with_conf_slug(self):
        url = reverse('vendor_review',
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})

        self.assertEqual(200, response.status_code)
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
