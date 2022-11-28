import gbe.models as conf
from django.test import (
    TestCase,
    Client,
)
from django.urls import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
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


class TestReviewClassList(TestCase):
    '''Tests for review_class_list view'''
    view_name = 'class_review_list'

    @classmethod
    def setUpTestData(cls):
        cls.performer = PersonaFactory()
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Class Reviewers')
        cls.conference = current_conference()
        ClassFactory.create_batch(4,
                                  b_conference=cls.conference,
                                  submitted=True)

    def setUp(self):
        self.client = Client()

    def test_review_class_all_well(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class Proposals')
        self.assertNotContains(response, "Accept &amp; Schedule")

    def test_review_class_w_scheduling(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class Proposals')
        self.assertContains(response, "Accept &amp; Schedule")

    def test_review_accepted_class_w_scheduling(self):
        ClassFactory(
            accepted=3,
            b_conference=self.conference,
            submitted=True)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class Proposals')
        self.assertContains(response, "Add to Schedule")

    def test_review_class_bad_user(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertEqual(response.status_code, 403)

    def test_review_class_no_profile(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertEqual(response.status_code, 403)

    def test_review_class_inactive_user(self):
        ClassFactory(
            teacher__contact__user_object__is_active=False,
            b_conference=self.conference,
            submitted=True)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, 'gbe-table-row gbe-table-danger')
