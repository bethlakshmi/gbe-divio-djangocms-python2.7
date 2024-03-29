from django.urls import reverse
from django.test import TestCase, override_settings
from django.test import Client
from tests.factories.gbe_factories import ProfileFactory
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_queued_email,
    grant_privilege,
    is_login_page,
    login_as,
    setup_admin_w_privs,
)
from tests.contexts.class_context import (
    ClassContext,
)
from gbetext import send_email_success_msg
from django.contrib.auth.models import User


class TestMailToPerson(TestCase):
    view_name = 'mail_to_individual'
    priv_list = ['Registrar',
                 'Volunteer Coordinator',
                 'Act Coordinator',
                 'Vendor Coordinator',
                 'Ticketing - Admin']

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs(['Registrar'])
        cls.privileged_profile = cls.privileged_user.profile
        cls.url = reverse(cls.view_name, urlconf="gbe.email.urls")
        cls.to_profile = ProfileFactory()
        cls.url = reverse(cls.view_name,
                          urlconf="gbe.email.urls",
                          args=[cls.to_profile.pk])

    def setUp(self):
        self.client = Client()

    def reduced_login(self):
        reduced_profile = ProfileFactory()
        grant_privilege(
            reduced_profile.user_object,
            'Registrar')
        login_as(reduced_profile, self)
        return reduced_profile

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "%s?next=%s" % (reverse('login'), self.url)
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_full_login_first_get(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '%s &lt;%s&gt;' % (
                self.to_profile.display_name,
                self.to_profile.user_object.email))

    def test_bad_profile(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.email.urls",
            args=[self.to_profile.pk+100]), follow=True)
        self.assertEqual(404, response.status_code)

    def test_alt_permissions(self):
        for priv in self.priv_list:
            privileged_profile = ProfileFactory()
            grant_privilege(privileged_profile.user_object,
                            priv)
            login_as(privileged_profile, self)
            response = self.client.get(self.url, follow=True)
            self.assertContains(
                response,
                '%s &lt;%s&gt;' % (
                    self.to_profile.display_name,
                    self.to_profile.user_object.email))

    def test_pick_admin_has_sender(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            ('<input type="email" name="sender" value="%s" ' +
             'maxlength="320" id="id_sender">') % (
                self.privileged_profile.user_object.email),
            html=True)
        self.assertContains(
            response,
            ('<input type="text" name="sender_name" value="%s" ' +
             'maxlength="150" id="id_sender_name">') % (
                self.privileged_profile.display_name),
            html=True)

    def test_pick_no_admin_fixed_email(self):
        reduced_profile = self.reduced_login()
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<input type="hidden" name="sender" ' +
            'value="%s" id="id_sender" />' % (
                reduced_profile.user_object.email),
            html=True)
        self.assertContains(
            response,
            ('<input type="hidden" name="sender_name" value="%s" ' +
             'id="id_sender_name">') % (
                reduced_profile.display_name),
            html=True)

    def test_send_email_success_status(self):
        login_as(self.privileged_profile, self)
        data = {
            'to': self.to_profile.user_object.email,
            'sender': "sender@admintest.com",
            'sender_name': "Sender Name",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_alert_exists(
            response, 'success', 'Success', "%s%s" % (
                send_email_success_msg,
                self.to_profile.user_object.email))

    def test_send_email_success_email_sent(self):
        login_as(self.privileged_profile, self)
        data = {
            'to': self.to_profile.user_object.email,
            'sender': "sender@admintest.com",
            'sender_name': "Sender Name",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_queued_email(
            [self.to_profile.user_object.email, ],
            data['subject'],
            data['html_message'],
            data['sender'],
            data['sender_name']
            )

    def test_send_email_reduced_w_fixed_from(self):
        reduced_profile = self.reduced_login()
        data = {
            'to': self.to_profile.user_object.email,
            'sender': "sender@admintest.com",
            'sender_name': "Sender Name",
            'subject': "Subject",
            'html_message': "<p>Test Message</p>",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        assert_queued_email(
            [self.to_profile.user_object.email, ],
            data['subject'],
            data['html_message'],
            reduced_profile.user_object.email,
            reduced_profile.display_name,
            )

    def test_send_email_failure(self):
        login_as(self.privileged_profile, self)
        data = {
            'sender': "sender@admintest.com",
            'html_message': "<p>Test Message</p>",
            'send': True
        }
        response = self.client.post(self.url, data=data, follow=True)
        self.assertContains(response, "This field is required.")
