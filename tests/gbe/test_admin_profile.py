import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.models import Profile


class TestAdminProfile(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'admin_profile'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    def get_form(self, invalid=False):
        data = {'first_name': 'new first',
                'last_name': 'new last',
                'display_name': 'Display P. Name',
                'email': 'new@last.com',
                'purchase_email': 'new@last.com',
                'address1': '789 Elm St',
                'address2': 'Apt. e',
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
            del(data['first_name'])
        return data

    def test_admin_profile_no_such_profile(self):
        no_such_id = Profile.objects.latest('pk').pk + 1
        url = reverse(self.view_name,
                      args=[no_such_id],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(404, response.status_code)

    def test_get(self):
        profile = self.performer.contact
        ProfilePreferencesFactory(profile=profile)

        url = reverse(self.view_name,
                      args=[profile.pk],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(200, response.status_code)

    def test_post_valid_form(self):
        profile = self.performer.contact
        ProfilePreferencesFactory(profile=profile)

        url = reverse(self.view_name,
                      args=[profile.pk],
                      urlconf="gbe.urls")
        data = self.get_form()
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data, follow=True)
        nt.assert_true(('http://testserver/profile/manage', 302) in
                       response.redirect_chain)
        nt.assert_equal(200, response.status_code)

    def test_post_invalid_form(self):
        profile = self.performer.contact
        ProfilePreferencesFactory(profile=profile)

        url = reverse(self.view_name,
                      args=[profile.pk],
                      urlconf="gbe.urls")
        data = self.get_form(invalid=True)
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=data)
        nt.assert_true('Your Profile' in response.content)
        nt.assert_equal(200, response.status_code)
