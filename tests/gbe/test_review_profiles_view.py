from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    ProfileFactory,
    TroupeFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from gbe.models import Profile
from tests.contexts import StaffAreaContext


class TestReviewProfiles(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'manage_users'

    def setUp(self):
        self.client = Client()
        self.profile = ProfilePreferencesFactory(
            profile__purchase_email='test@test.com').profile
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')
        self.url = reverse('manage_users',
                           urlconf='gbe.urls')

    def test_non_privileged_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_past_staff_lead(self):
        context = StaffAreaContext()
        context.conference.status = "completed"
        context.conference.save()
        login_as(context.staff_lead, self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_no_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login', urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_staff_lead(self):
        context = StaffAreaContext()
        login_as(context.staff_lead, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Manage Users")

    def test_contact_info(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.profile.purchase_email)
        self.assertContains(response, self.profile.user_object.email)
        self.assertContains(response, self.profile.phone)

    def test_with_troupe(self):
        troupe = TroupeFactory(contact=self.profile)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, troupe.name)

    def test_special_registrar(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, "/profile/admin/")
        self.assertContains(response, "/profile/delete/")

    def test_special_not_registrar(self):
        coordinator = ProfileFactory().user_object
        grant_privilege(coordinator, 'Volunteer Coordinator')
        login_as(coordinator, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, "/profile/admin/")
        self.assertNotContains(response, "/profile/delete/")
