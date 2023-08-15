from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestMergeProfileSelect(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'start_merge_users'

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfilePreferencesFactory(
            profile__purchase_email='test@test.com').profile
        cls.avail_profile = ProfileFactory()
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Registrar')
        cls.url = reverse(cls.view_name,
                          urlconf='gbe.urls',
                          args=[cls.profile.pk])

    def test_no_privilege(self):
        random_user = ProfileFactory().user_object
        login_as(random_user, self)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_exclude_two_profiles(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Merge Users - Pick Second')
        self.assertNotContains(response, self.privileged_user.email)
        self.assertNotContains(response, self.profile.user_object.email)
        self.assertContains(response, self.avail_profile.user_object.email)
