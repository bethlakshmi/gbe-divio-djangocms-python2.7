from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from django.test import (
    TestCase,
    Client,
)
from django.core.urlresolvers import reverse
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

from django.core.exceptions import PermissionDenied


class TestReviewClassList(TestCase):
    '''Tests for review_class_list view'''
    view_name = 'class_review_list'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Class Reviewers')
        self.conference = current_conference()
        ClassFactory.create_batch(4,
                                  b_conference=self.conference,
                                  e_conference=self.conference,
                                  submitted=True)

    def test_review_class_all_well(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_class_bad_user(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        nt.assert_equal(response.status_code, 403)

    def test_review_class_no_profile(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        nt.assert_equal(response.status_code, 403)

    def test_review_class_inactive_user(self):
        ClassFactory(
            teacher__contact__user_object__is_active=False,
            b_conference=self.conference,
            e_conference=self.conference,
            submitted=True)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertIn('bid-table danger', response.content)
