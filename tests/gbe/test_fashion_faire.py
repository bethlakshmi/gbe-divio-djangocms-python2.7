from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    VendorFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as


class TestFashionFaireView(TestCase):
    view_name = 'fashion_faire'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def test_fashion_faire_no_login(self):
        proposal = VendorFactory(submitted=True, accepted=3)
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, proposal.b_title)

    def test_filter_by_conference(self):
        conference = ConferenceFactory(status='upcoming')
        otherconf = ConferenceFactory()
        proposal = VendorFactory(b_conference=conference,
                                 accepted=3)

        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url,
                                   data={'conference': conference})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, proposal.b_title)
        self.assertContains(
            response,
            '<div class="col-lg-4 col-md-6 col-sm-12 col-12">')
        self.assertNotContains(response, 'Featured Vendors')

    def test_filter_by_conference_default(self):
        conference = ConferenceFactory(status='upcoming')
        otherconf = ConferenceFactory()
        proposal = VendorFactory(b_conference=conference,
                                 accepted=3)
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, proposal.b_title)

    def test_featured_vendor(self):
        conference = ConferenceFactory(status='upcoming')
        proposal = VendorFactory(b_conference=conference,
                                 accepted=3,
                                 level="Featured")
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url,
                                   data={'conference': conference})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, proposal.b_title)
        self.assertContains(
            response,
            '<div class="col-lg-6 col-sm-12 col-12">')
        self.assertContains(response, 'Featured Vendors')
