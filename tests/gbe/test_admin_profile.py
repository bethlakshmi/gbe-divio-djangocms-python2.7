from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    BioFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.models import Profile
from gbetext import admin_note


class TestAdminProfile(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'admin_profile'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.performer = BioFactory()
        cls.privileged_user = ProfileFactory().user_object
        cls.privileged_user.pageuser.created_by_id = cls.privileged_user.pk
        cls.privileged_user.pageuser.save()
        grant_privilege(cls.privileged_user, 'Registrar')

    def get_form(self, invalid=False):
        data = {'first_name': 'new first',
                'last_name': 'new last',
                'display_name': 'Display P. Name',
                'email': 'new@last.com',
                'purchase_email': 'new@last.com',
                'city': 'Konigsburg',
                'state': 'PA',
                'zip_code': '23456',
                'country': 'USA',
                'phone': '617-555-2121',
                'best_time': 'Any',
                'how_heard': 'Facebook',
                'prefs-inform_about': 'Performing',
                'in_hotel': True,
                'show_hotel_infobox': False}
        if invalid:
            del(data['email'])
        return data

    def test_admin_profile_no_such_profile(self):
        no_such_id = Profile.objects.latest('pk').pk + 1
        url = reverse(self.view_name,
                      args=[no_such_id],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_get(self):
        profile = self.performer.contact
        ProfilePreferencesFactory(profile=profile)

        url = reverse(self.view_name,
                      args=[profile.pk],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            '<input type="submit" value="Update User Account" ' +
            'class="btn gbe-btn-primary">',
            html=True)
        self.assertContains(
            response,
            admin_note)
        self.assertContains(
            response,
            "<title>Update User Profile</title")

    def test_post_valid_form(self):
        profile = self.performer.contact
        ProfilePreferencesFactory(profile=profile)

        url = "%s?next=%s" % (
            reverse(self.view_name, args=[profile.pk], urlconf="gbe.urls"),
            reverse('manage_users', urlconf='gbe.urls'))
        data = self.get_form()
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(response,
                             reverse('manage_users', urlconf='gbe.urls'))
        self.assertContains(
            response,
            "Updated Profile: %s" % data['display_name'])

    def test_post_invalid_form(self):
        profile = self.performer.contact
        ProfilePreferencesFactory(profile=profile)

        url = reverse(self.view_name,
                      args=[profile.pk],
                      urlconf="gbe.urls")
        data = self.get_form(invalid=True)
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data)
        self.assertContains(response, 'There is an error on the form.')
