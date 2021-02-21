from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    PersonaFactory,
    ProfilePreferencesFactory,
    TroupeFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from gbe.models import Troupe
from tests.contexts import StaffAreaContext


class TestReviewTroupes(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'manage_troupes'

    def setUp(self):
        self.client = Client()
        self.profile = ProfilePreferencesFactory(
            profile__purchase_email='test@test.com').profile
        self.troupe = TroupeFactory(contact=self.profile)
        self.member = PersonaFactory()
        self.troupe.membership.add(self.member)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')
        self.url = reverse(self.view_name, urlconf='gbe.urls')

    def test_non_privileged_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_no_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login', urlconf='gbe.urls') + "/?next=" + self.url
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
            ('<a href="%s" data-toggle="tooltip" title="%s">' +
             '<button type="button" class="btn btn-default btn-sm">' +
             '<i class="icon-eye"></i></button></a>') % (
             reverse('admin_landing_page',
                     urlconf='gbe.urls',
                     args=[self.troupe.contact.resourceitem_id]),
             "View Contact Landing Page"),
            html=True)
        self.assertContains(
            response,
            ('<a href="%s" data-toggle="tooltip" title="%s">' +
             '<button type="button" class="btn btn-default btn-sm">' +
             '<i class="icon-envelope"></i></button></a>') % (
             reverse('mail_to_individual',
                     urlconf='gbe.email.urls',
                     args=[self.troupe.contact.resourceitem_id]),
             "Email Contact"),
            html=True)
        self.assertContains(
            response,
            ('<a href="%s" data-toggle="tooltip" title="%s">' +
             '<button type="button" class="btn btn-default btn-sm">' +
             '<i class="far fa-eye"></i></button></a>') % (
             reverse('troupe_view',
                     urlconf='gbe.urls',
                     args=[self.troupe.resourceitem_id]),
             "View Troupe"),
            html=True)
