from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
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
    bad_token_msg,
    default_update_profile_msg,
    email_pref_note,
    link_sent_msg,
    send_link_message,
)
import os
from django.contrib.sites.models import Site
from gbe.email.functions import create_unsubscribe_link
from django.utils.html import escape


class TestEditEmail(TestCase):
    '''Tests for update_profile  view'''
    view_name = 'email_update'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.profile = ProfilePreferencesFactory().profile
        self.url = reverse(self.view_name, urlconf='gbe.urls')
        os.environ['RECAPTCHA_DISABLE'] = 'True'

    def test_update_email_no_token(self):
        response = self.client.get(self.url)
        self.assertContains(response, bad_token_msg)
        self.assertContains(response, "Email:")

    def test_update_email_bad_token(self):
        self.url = reverse(
            self.view_name,
            urlconf='gbe.urls',
            args=["%s:%s" % (self.profile.user_object.email, "badsignature")])
        response = self.client.get(self.url)
        self.assertContains(response, bad_token_msg)
        self.assertContains(response, "Email:")

    def test_update_email_bad_user(self):
        self.url = create_unsubscribe_link("emailedit@doesnotexist.com")
        response = self.client.get(self.url)
        self.assertContains(response, bad_token_msg)
        self.assertContains(response, "Email:")

    def test_update_email_good_token(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            )+ "?email_disable=send_schedule_change_notifications"
        response = self.client.get(self.url)
        self.assertContains(response, escape(email_pref_note))
        self.assertContains(response, "Email Options")
        self.assertNotContains(response, "Email:")
        self.assertContains(
            response,
            '<input type="checkbox" ' +
            'name="send_schedule_change_notifications"' +
            ' id="id_send_schedule_change_notifications" />')
        self.assertContains(
            response, "shadow-red")

    def test_update_email_missing_preferences(self):
        profile = ProfileFactory()
        self.url = create_unsubscribe_link(profile.user_object.email)
        response = self.client.get(self.url)
        self.assertContains(response, escape(email_pref_note))
        self.assertContains(response, "Email Options")
        self.assertNotContains(response, "Email:")

    def tearDown(self):
        del os.environ['RECAPTCHA_DISABLE']

'''
    def test_update_email_pref_no_login(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'id="recaptcha-verification"')
        self.assertContains(response, email_pref_note.replace("'", "&#39;"))

    def test_update_email_post_valid_form(self):
        response = self.client.post(self.url,
                                    data=self.get_form(),
                                    follow=True)
        site = Site.objects.get_current()
        self.assertRedirects(response, "http://%s" % site.domain)
        preferences = ProfilePreferences.objects.get(profile=self.profile)
        self.assertTrue(preferences.send_daily_schedule)
        self.assertFalse(preferences.send_bid_notifications)
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
