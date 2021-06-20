from django.test import TestCase
from django.test import Client
from django.urls import reverse
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
from post_office.models import Email
from django.conf import settings
from django.core.signing import TimestampSigner


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
        self.assertContains(response, send_link_message)

    def test_update_email_bad_token(self):
        self.url = reverse(
            self.view_name,
            urlconf='gbe.urls',
            args=["%s:%s" % (self.profile.user_object.email, "badsignature")])
        response = self.client.get(self.url)
        self.assertContains(response, bad_token_msg)
        self.assertContains(response, send_link_message)

    def test_update_email_bad_user(self):
        self.url = create_unsubscribe_link("emailedit@doesnotexist.com")
        response = self.client.get(self.url)
        self.assertContains(response, bad_token_msg)
        self.assertContains(response, send_link_message)

    def test_update_email_good_token(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            ) + "?email_disable=send_schedule_change_notifications"
        response = self.client.get(self.url)
        self.assertContains(response, escape(email_pref_note))
        self.assertContains(response, "Email Options")
        self.assertNotContains(response, "Email:")
        self.assertContains(
            response,
            '<input type="checkbox" ' +
            'name="send_schedule_change_notifications"' +
            ' id="id_send_schedule_change_notifications" />',
            html=True)
        self.assertContains(
            response, "shadow-highlight")

    def test_update_email_missing_preferences(self):
        profile = ProfileFactory()
        self.url = create_unsubscribe_link(profile.user_object.email)
        response = self.client.get(self.url)
        self.assertContains(response, escape(email_pref_note))
        self.assertContains(response, "Email Options")
        self.assertNotContains(response, "Email:")

    def test_update_email_post_valid_user_email(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            )
        response = self.client.post(
            self.url,
            data={'email': self.profile.user_object.email},
            follow=True)
        assert_alert_exists(
            response, 'success', 'Success', link_sent_msg)
        queued_email = Email.objects.filter(
            status=2,
            to=self.profile.user_object.email,
            subject="Unsubscribe from GBE Mail",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)

    def test_update_email_post_invalid_user_email(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            )
        response = self.client.post(
            self.url,
            data={'email': self.profile.user_object.email + "invalid"},
            follow=True)
        assert_alert_exists(
            response, 'success', 'Success', link_sent_msg)
        queued_email = Email.objects.filter(
            status=2,
            to=self.profile.user_object.email,
            subject="Unsubscribe from GBE Mail",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)

    def test_update_email_post_inactive_profile_email(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            )
        self.profile.user_object.is_active = False
        self.profile.user_object.save()
        response = self.client.post(
            self.url,
            data={'email': self.profile.user_object.email},
            follow=True)
        assert_alert_exists(
            response, 'success', 'Success', link_sent_msg)
        queued_email = Email.objects.filter(
            status=2,
            to=self.profile.user_object.email,
            subject="Unsubscribe from GBE Mail",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)

    def test_update_email_post_valid_form_w_token(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            ) + "?email_disable=send_schedule_change_notifications"
        response = self.client.post(self.url, follow=True, data={
            'token': TimestampSigner().sign(self.profile.user_object.email),
            'send_daily_schedule': True,
            'send_bid_notifications': False,
            'send_role_notifications': False,
            'send_schedule_change_notifications': True})
        site = Site.objects.get_current()
        self.assertRedirects(response, "http://%s" % site.domain)
        preferences = ProfilePreferences.objects.get(profile=self.profile)
        self.assertTrue(preferences.send_daily_schedule)
        self.assertFalse(preferences.send_bid_notifications)
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    def test_update_email_post_valid_form_logged_in(self):
        login_as(self.profile.user_object, self)
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            ) + "?email_disable=send_schedule_change_notifications"
        response = self.client.post(self.url, follow=True, data={
            'token': TimestampSigner().sign(self.profile.user_object.email),
            'send_daily_schedule': True,
            'send_bid_notifications': False,
            'send_role_notifications': False,
            'send_schedule_change_notifications': True})
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        preferences = ProfilePreferences.objects.get(profile=self.profile)
        self.assertTrue(preferences.send_daily_schedule)
        self.assertFalse(preferences.send_bid_notifications)
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    def test_update_email_post_valid_form_w_bad_token(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            ) + "?email_disable=send_schedule_change_notifications"
        response = self.client.post(self.url, follow=True, data={
            'token': "bad, bad token",
            'send_daily_schedule': True,
            'send_bid_notifications': False,
            'send_role_notifications': False,
            'send_schedule_change_notifications': True})
        self.assertContains(response, send_link_message)

    def test_update_email_post_valid_form_w_no_pref(self):
        pref = ProfilePreferences.objects.get(profile=self.profile)
        pref.delete()
        self.url = create_unsubscribe_link(
            self.profile.user_object.email
            ) + "?email_disable=send_schedule_change_notifications"
        response = self.client.post(self.url, follow=True, data={
            'token': TimestampSigner().sign(self.profile.user_object.email),
            'send_daily_schedule': True,
            'send_bid_notifications': False,
            'send_role_notifications': False,
            'send_schedule_change_notifications': True})
        site = Site.objects.get_current()
        self.assertRedirects(response, "http://%s" % site.domain)
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    def test_update_email_post_invalid_form_wout_token(self):
        self.url = create_unsubscribe_link(
            self.profile.user_object.email,
            disable="send_schedule_change_notifications")
        response = self.client.post(self.url, follow=True, data={},)
        self.assertContains(response, send_link_message)

    def tearDown(self):
        del os.environ['RECAPTCHA_DISABLE']
