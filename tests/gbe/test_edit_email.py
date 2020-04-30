from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.contexts import VolunteerContext
from tests.factories.gbe_factories import (
    ProfileFactory,
    ProfilePreferencesFactory,
    UserFactory,
    UserMessageFactory
)
from gbe.models import (
    Conference,
    ProfilePreferences,
    UserMessage
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as
)
from gbetext import (
    default_update_profile_msg,
    email_pref_note,
)
import os
from django.contrib.sites.models import Site


class TestEditEmail(TestCase):
    '''Tests for update_profile  view'''
    view_name = 'email_update'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.profile = ProfilePreferencesFactory().profile
        self.url = reverse(self.view_name, urlconf='gbe.urls')
        os.environ['RECAPTCHA_DISABLE'] = 'True'

    def get_form(self, invalid=False):
        data = {'email': self.profile.user_object.email,
                'send_daily_schedule': True,
                'send_bid_notifications': False,
                'send_role_notifications': False,
                'send_schedule_change_notifications': True, }
        if invalid:
            del(data['email'])
        return data

    def test_update_email_no_preferences(self):
        profile = ProfileFactory()
        data = self.get_form()
        data['email'] = profile.user_object.email
        print(profile.user_object.email)
        response = self.client.post(self.url,
                                    data=self.get_form(),
                                    follow=True)
        preferences = ProfilePreferences.objects.get(profile=profile)
        self.assertTrue(preferences.send_daily_schedule)
        self.assertFalse(preferences.send_bid_notifications)

    def tearDown(self):
        del os.environ['RECAPTCHA_DISABLE']

'''
    def test_update_email_pref_no_login(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'id="recaptcha-verification"')
        self.assertContains(response, email_pref_note.replace("'", "&#39;"))

    def test_update_email_disable_email(self):
        url = self.url + "?email_disable=send_schedule_change_notifications"
        response = self.client.get(url)
        self.assertContains(
            response,
            '<input type="checkbox" ' +
            'name="send_schedule_change_notifications"' +
            ' id="id_send_schedule_change_notifications" />')
        self.assertContains(
            response, "shadow-red")

    def test_update_email_post_valid_form(self):
        response = self.client.post(self.url,
                                    data=self.get_form(),
                                    follow=True)
        site = Site.objects.get_current()
        self.assertRedirects(response, "http://%s" % site.domain)
        preferences = ProfilePreferences.objects.get(profile=self.profile)
        self.assertTrue(preferences.send_daily_schedule)
        self.assertFalse(preferences.send_bid_notifications)
        print(response.content)
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    def test_update_email_post_valid_form_w_login(self):
        login_as(self.profile.user_object, self)
        response = self.client.post(self.url,
                                    data=self.get_form(),
                                    follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        preferences = ProfilePreferences.objects.get(profile=self.profile)
        self.assertTrue(preferences.send_daily_schedule)
        self.assertFalse(preferences.send_bid_notifications)
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    def test_post_invalid_form(self):
        response = self.client.post(self.url,
                                    data=self.get_form(invalid=True),
                                    follow=True)
        self.assertContains(response, "Update Email Preferences")
        self.assertContains(response, "This field is required.")
        self.assertEqual(response.status_code, 200)
'''
