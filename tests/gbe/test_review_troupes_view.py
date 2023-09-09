from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ProfileFactory,
    ProfilePreferencesFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.functions.scheduler_functions import get_or_create_bio
from tests.contexts import ShowContext


class TestReviewTroupes(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'manage_troupes'

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfilePreferencesFactory(
            profile__purchase_email='test@test.com').profile
        cls.troupe = BioFactory(contact=cls.profile,
                                multiple_performers=True)
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Registrar')
        cls.url = reverse(cls.view_name, urlconf='gbe.urls')

    def test_non_privileged_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_no_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('login') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_all_well(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Manage Troupes")
        self.assertContains(response, self.troupe.name)
        self.assertContains(response, self.profile.display_name)
        self.assertContains(response, self.profile.user_object.email)
        self.assertContains(
            response,
            '<a class="dropdown-item" href="%s">%s</a>' % (
             reverse('admin_landing_page',
                     urlconf='gbe.urls',
                     args=[self.troupe.contact.pk]),
             "View Contact Landing Page"),
            html=True)
        self.assertContains(
            response,
            '<a class="dropdown-item" href="%s">%s</a>' % (
             reverse('mail_to_individual',
                     urlconf='gbe.email.urls',
                     args=[self.troupe.contact.pk]),
             "Email Contact"),
            html=True)
        self.assertContains(
            response,
            '<a class="dropdown-item" href="%s">%s</a>' % (
             reverse('bio_view',
                     urlconf='gbe.urls',
                     args=[self.troupe.pk]),
             "View Troupe"),
            html=True)

    def test_show_member(self):
        context = ShowContext(performer=self.troupe)
        member = ProfileFactory()
        context.people.users.add(member.user_object)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.troupe.name)
        self.assertContains(response, self.profile.display_name)
        self.assertContains(response, self.profile.user_object.email)
        self.assertContains(response, member.display_name)

