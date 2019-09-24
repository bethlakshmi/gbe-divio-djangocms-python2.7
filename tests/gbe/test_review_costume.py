from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
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

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Costume Reviewers')
        self.coordinator = ProfileFactory()
        grant_privilege(self.coordinator, 'Costume Reviewers')
        grant_privilege(self.coordinator, 'Costume Coordinator')

    def get_form(self, bid, evaluator, invalid=False):
        data = {'vote': 3,
                'notes': "Foo",
                'bid': bid.pk,
                'evaluator': evaluator.pk}
        if invalid:
            del(data['vote'])
        return data

    def test_review_costume_all_well(self):
        costume = CostumeFactory(performer=self.performer)
        other_performer = PersonaFactory()
        url = reverse(self.view_name, args=[costume.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
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
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Review Information' in response.content)

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
        response = self.client.get(url)
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
        html_tag = '<h2 class="review-title">%s</h2>'
        title_string = ("Bid Information for %s" %
                        bid.b_conference.conference_name)
        html_title = html_tag % title_string
        assert html_title in response.content

    def test_review_costume_no_performer(self):
        costume = CostumeFactory()
        url = reverse(self.view_name, args=[costume.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
