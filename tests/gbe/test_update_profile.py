from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.contexts import VolunteerContext
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    UserFactory,
    UserMessageFactory
)
from gbe.models import (
    Conference,
    UserMessage
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as
)
from gbetext import default_update_profile_msg


class TestUpdateProfile(TestCase):
    '''Tests for update_profile  view'''
    view_name = 'profile_update'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.counter = 0

    def get_form(self, invalid=False):
        self.counter += 1
        email = "new%d@last.com" % self.counter
        data = {'first_name': 'new first',
                'last_name': 'new last',
                'display_name': 'Display P. Name',
                'email': email,
                'purchase_email': email,
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

    def post_profile(self, redirect=None, form=None):
        profile = ProfilePreferencesFactory().profile

        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        if redirect:
            url = url + "?next=" + redirect
        login_as(profile, self)
        if not form:
            data = self.get_form()
        else:
            data = form
        response = self.client.post(url, data=data, follow=True)
        return response

    def test_update_profile_no_such_profile(self):
        user = UserFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        self.assertTrue(user.profile is not None)

    def test_update_profile_no_display_name(self):
        pref = ProfilePreferencesFactory(profile__display_name="")
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(pref.profile.user_object, self)
        response = self.client.get(url)
        self.assertTrue(
            "%s %s" % (
                pref.profile.user_object.first_name,
                pref.profile.user_object.last_name) in response.content)

    def test_update_profile_how_heard(self):
        pref = ProfilePreferencesFactory(
            profile__how_heard="[u'Word of mouth']")
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(pref.profile.user_object, self)
        response = self.client.get(url)
        self.assertTrue(
            '<input checked="checked" id="id_how_heard_6" name="how_heard" ' +
            'type="checkbox" value="Word of mouth" />' in response.content)

    def test_update_profile_post_empty_display_name(self):
        data = self.get_form()
        data['display_name'] = ""
        data['purchase_email'] = ""
        response = self.post_profile(form=data)
        self.assertTrue(
            "%s %s" % (data['first_name'].title(),
                       data['last_name'].title()) in response.content)

    def test_update_profile_post_cleanup_display_name(self):
        data = self.get_form()
        data['display_name'] = " trim me   nocaps"
        response = self.post_profile(form=data)
        self.assertTrue(
            "Trim Me Nocaps" in response.content)

    def test_update_profile_post_valid_form(self):
        response = self.post_profile()
        self.assertTrue("Your Account" in response.content)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))

    def test_update_profile_post_valid_redirect(self):
        context = VolunteerContext()
        context.conference.accepting_bids = True
        context.conference.save()
        redirect = reverse('volunteer_create', urlconf='gbe.urls')
        response = self.post_profile(redirect=redirect)
        self.assertRedirects(response, redirect)

    def test_update_profile_post_invalid_form(self):
        profile = ProfilePreferencesFactory().profile

        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        data = self.get_form(invalid=True)
        response = self.client.post(url, data=data, follow=True)
        self.assertTrue("Update Profile" in response.content)
        self.assertEqual(response.status_code, 200)

    def test_update_profile_make_message(self):
        response = self.post_profile()
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    def test_update_profile_has_message(self):
        msg = UserMessageFactory(
            view='UpdateProfileView',
            code='UPDATE_PROFILE')
        response = self.post_profile()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
