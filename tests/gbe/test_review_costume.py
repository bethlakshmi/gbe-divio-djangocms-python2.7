from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    CostumeFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    bad_id_for,
    grant_privilege,
    is_login_page,
    login_as,
)
from gbe.models import Costume


class TestReviewCostume(TestCase):
    '''Tests for review_costume view'''
    view_name = "costume_review"

    @classmethod
    def setUpTestData(cls):
        cls.performer = PersonaFactory()
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Costume Reviewers')
        cls.coordinator = ProfileFactory()
        grant_privilege(cls.coordinator, 'Costume Reviewers')
        grant_privilege(cls.coordinator, 'Costume Coordinator')

    def setUp(self):
        self.client = Client()

    def get_form(self, bid, evaluator):
        data = {'vote': 3,
                'notes': "Foo",
                'bid': bid.pk,
                'evaluator': evaluator.pk}
        return data

    def test_review_costume_all_well(self):
        costume = CostumeFactory(performer=self.performer)
        other_performer = PersonaFactory()
        url = reverse(self.view_name, args=[costume.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Costume Proposal')
        self.assertContains(response, self.performer.name)
        self.assertNotContains(response, other_performer.name)

    def test_review_costume_past_conference(self):
        conference = ConferenceFactory(status='completed')
        costume = CostumeFactory(b_conference=conference,
                                 performer=self.performer)
        url = reverse(self.view_name, args=[costume.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('costume_view',
                    urlconf='gbe.urls',
                    args=[costume.pk]))
        self.assertContains(response, 'Costume Proposal')
        self.assertNotContains(response, 'Review Information')

    def test_no_login_redirects_to_login(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_costume_id(self):
        login_as(ProfileFactory(), self)
        bad_id = bad_id_for(Costume)
        url = reverse(self.view_name, args=[bad_id], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_review_costume_post_valid(self):
        bid = CostumeFactory(performer=self.performer)
        url = reverse(self.view_name,
                      args=[bid.pk],
                      urlconf='gbe.urls')
        login_as(self.coordinator, self)
        data = self.get_form(bid, self.coordinator)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, bid.b_conference.conference_name)

    def test_review_costume_no_performer(self):
        costume = CostumeFactory()
        url = reverse(self.view_name, args=[costume.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Costume Proposal')
        self.assertContains(response, 'Review Costume')

    def test_view_costume_how_heard(self):
        '''view_costume view, success
        '''
        profile = ProfileFactory(how_heard=['Word of mouth'])
        costume = CostumeFactory(profile=profile)
        url = reverse(self.view_name, urlconf="gbe.urls", args=[costume.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertContains(response, profile.how_heard[0])
