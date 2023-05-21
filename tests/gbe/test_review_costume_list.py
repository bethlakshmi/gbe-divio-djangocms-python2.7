from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    CostumeFactory,
    ConferenceFactory,
    ProfileFactory,
    UserFactory,
    )
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestReviewCostumeList(TestCase):
    '''Tests for review_costume_list view'''
    view_name = "costume_review_list"

    @classmethod
    def setUpTestData(cls):
        cls.performer = BioFactory()
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Costume Reviewers')
        cls.conference = ConferenceFactory(status='upcoming',
                                           accepting_bids=True)
        cls.costumes = CostumeFactory.create_batch(
            4,
            b_conference=cls.conference,
            submitted=True)

    def setUp(self):
        self.client = Client()

    def test_review_costume_all_well(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Costume Proposals')
        for bid in self.costumes:
            self.assertContains(response, bid.b_title)

    def test_review_costume_w_performer(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        costume = CostumeFactory(bio=self.performer,
                                 b_conference=self.conference,
                                 submitted=True)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Costume Proposals')
        self.assertContains(response, costume.b_title)
        self.assertContains(response, self.performer.name)

    def test_review_costume_bad_user(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertEqual(403, response.status_code)

    def test_review_costume_no_profile(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertEqual(403, response.status_code)

    def test_review_costume_no_conf_slug(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)
        for acostume in self.costumes:
            self.assertContains(response, acostume.b_title)

    def test_review_costume_inactive_user(self):
        self.costumes = CostumeFactory(
            b_conference=self.conference,
            submitted=True,
            profile__user_object__is_active=False)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, 'gbe-table-row gbe-table-danger')
