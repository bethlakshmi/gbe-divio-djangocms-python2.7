from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.functions import validate_profile


class TestProfileAutoComplete(TestCase):
    url = reverse('profile-autocomplete')

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory().user_object
        grant_privilege(self.user, 'Scheduling Mavens')

    def test_list_profile(self):
        profile = ProfileFactory()
        login_as(self.user, self)
        response = self.client.get(self.url)
        self.assertContains(response, profile.display_name)
        self.assertContains(response, profile.pk)

    def test_no_access_profile(self):
        profile = ProfileFactory()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_list_profile_w_search_by_display_name(self):
        profile1 = ProfileFactory()
        profile2 = ProfileFactory()
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            profile1.display_name))
        self.assertContains(response, profile1.display_name)
        self.assertContains(response, profile1.pk)
        self.assertNotContains(response, profile2.display_name)

    def test_list_profile_w_search_by_username(self):
        profile1 = ProfileFactory()
        profile2 = ProfileFactory()
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            profile1.user_object.username))
        self.assertContains(response, profile1.display_name)
        self.assertContains(response, profile1.pk)
        self.assertNotContains(response, profile2.display_name)

    def test_list_profile_w_search_by_first_name(self):
        profile1 = ProfileFactory()
        profile2 = ProfileFactory()
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            profile1.user_object.first_name))
        self.assertContains(response, profile1.display_name)
        self.assertContains(response, profile1.pk)
        self.assertNotContains(response, profile2.display_name)

    def test_list_profile_w_search_by_last_name(self):
        profile1 = ProfileFactory()
        profile2 = ProfileFactory(user_object=UserFactory(
            last_name="NOT HERE"))
        login_as(self.user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            profile1.user_object.last_name))
        self.assertContains(response, profile1.display_name)
        self.assertContains(response, profile1.pk)
        self.assertNotContains(response, profile2.display_name)
