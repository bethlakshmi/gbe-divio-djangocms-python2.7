from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import ProfileFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import warn_user_merge_delete
from gbe.models import Profile


class TestMergeProfileSelect(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'merge_profiles'
    counter = 0

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory()
        cls.avail_profile = ProfileFactory()
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Registrar')
        cls.url = reverse(cls.view_name,
                          urlconf='gbe.urls',
                          args=[cls.profile.pk, cls.avail_profile.pk])

    def get_form(self, invalid=False):
        self.counter += 1
        email = "new%d@last.com" % self.counter
        data = {'first_name': 'new first',
                'last_name': 'new last',
                'display_name': 'Display P. Name',
                'email': email,
                'purchase_email': email,
                'city': 'Konigsburg',
                'state': 'PA',
                'zip_code': '23456',
                'country': 'USA',
                'phone': '617-555-2121',
                'best_time': 'Any',
                'how_heard': 'Facebook',
                'prefs-inform_about': 'Performing',
                'in_hotel': True,
                'show_hotel_infobox': False,
                'email_pref-send_daily_schedule': True,
                'email_pref-send_bid_notifications': False,
                'email_pref-send_role_notifications': False,
                'email_pref-send_schedule_change_notifications': True, }
        if invalid:
            del(data['email'])
        return data

    def test_no_privilege(self):
        random_user = ProfileFactory().user_object
        login_as(random_user, self)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_get_form(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, 'Merge Users - Verify Info')
        self.assertContains(response, self.profile.user_object.email)
        self.assertContains(response, self.avail_profile.user_object.email)
        self.assertContains(response, reverse(
            self.view_name,
            urlconf='gbe.urls',
            args=[self.avail_profile.pk, self.profile.pk]))
        self.assertContains(
            response,
            ('<input type="text" name="purchase_email" value="%s" ' +
             'required id="id_purchase_email">'
             ) % self.profile.user_object.email,
            html=True)

    def test_warn_on_self(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf='gbe.urls',
            args=[self.profile.pk, self.privileged_user.profile.pk]))
        self.assertContains(response, 'Merge Users - Verify Info')
        self.assertContains(response, self.profile.user_object.email)
        self.assertContains(response, self.privileged_user.email)
        self.assertContains(response, reverse(
            self.view_name,
            urlconf='gbe.urls',
            args=[self.privileged_user.profile.pk, self.profile.pk]))
        self.assertContains(response, warn_user_merge_delete)

    def test_submit_success(self):
        login_as(self.privileged_user, self)
        data = self.get_form()
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, 'Merge Users - Merge Bios')
        updated_target = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(updated_target.display_name, data['display_name'])
        self.assertTrue(updated_target.preferences.send_daily_schedule)
        self.assertEqual(updated_target.preferences.inform_about,
                         "['Performing']")
