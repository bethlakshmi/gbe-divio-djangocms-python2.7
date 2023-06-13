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
from tests.contexts import StaffAreaContext


class TestReviewTroupes(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'manage_troupes'

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfilePreferencesFactory(
            profile__purchase_email='test@test.com').profile
        cls.troupe = BioFactory(contact=cls.profile,
                                multiple_performers=True)
        cls.member = ProfileFactory()
        people = get_or_create_bio(cls.troupe)
        people.users.add(cls.member.user_object)
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
        self.assertContains(response, self.member)
        self.assertContains(
            response,
            ('<a href="%s" data-toggle="tooltip" title="%s" class="btn ' +
             'gbe-btn-table btn-sm"><i class="far fa-eye"></i></a>') % (
             reverse('admin_landing_page',
                     urlconf='gbe.urls',
                     args=[self.troupe.contact.pk]),
             "View Contact Landing Page"),
            html=True)
        self.assertContains(
            response,
            ('<a href="%s" data-toggle="tooltip" title="%s" class="btn ' +
             'gbe-btn-table btn-sm"><i class="far fa-envelope"></i></a>') % (
             reverse('mail_to_individual',
                     urlconf='gbe.email.urls',
                     args=[self.troupe.contact.pk]),
             "Email Contact"),
            html=True)
        self.assertContains(
            response,
            ('<a href="%s" data-toggle="tooltip" title="%s" class="btn ' +
             'gbe-btn-table btn-sm"><i class="fas fa-users"></i></a>') % (
             reverse('troupe_view',
                     urlconf='gbe.urls',
                     args=[self.troupe.pk]),
             "View Troupe"),
            html=True)
