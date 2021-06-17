import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_email_template_used,
    grant_privilege,
    login_as,
)
import os
from mock import patch, Mock
import urllib
from django.core.files import File
from gbetext import found_on_list_msg
from django.conf import settings


class TestRegister(TestCase):
    '''Tests for register  view'''
    view_name = 'register'

    def setUp(self):
        self.client = Client()
        self.counter = 0
        os.environ['RECAPTCHA_DISABLE'] = 'True'

    def get_post_data(self):
        self.counter += 1
        email = "new%d@last.com" % self.counter
        data = {'username': 'test%d' % self.counter,
                'first_name': 'new first',
                'last_name': 'new last',
                'email': email,
                'password1': 'test',
                'password2': 'test'}
        return data

    def test_register_get(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        response = self.client.get(url, follow=True)
        self.assertContains(response, "Create an Account")

    @patch('urllib.request.urlopen', autospec=True)
    def test_register_post(self, m_urlopen):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertRedirects(
            response,
            reverse('profile_update', urlconf='gbe.urls'))

    @patch('urllib.request.urlopen', autospec=True)
    def test_register_redirect(self, m_urlopen):
        url = "%s?next=%s" % (
            reverse(self.view_name, urlconf='gbe.urls'),
            reverse('volunteer_signup', urlconf='gbe.scheduling.urls'))

        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertRedirects(response, "%s?next=%s" % (
            reverse('profile_update', urlconf='gbe.urls'),
            reverse('volunteer_signup', urlconf='gbe.scheduling.urls')))

    def test_register_post_nothing(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        response = self.client.post(url, {'data': 'bad'}, follow=True)
        self.assertContains(response, "This field is required.")

    def test_register_unique_email(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        post_data = self.get_post_data()
        profile = ProfileFactory(user_object__email=post_data['email'])
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "That email address is already in use")

    def tearDown(self):
        del os.environ['RECAPTCHA_DISABLE']

    @patch('urllib.request.urlopen', autospec=True)
    def test_register_spammer_email(self, m_urlopen):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response_bad.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertContains(response, found_on_list_msg)

    @patch('urllib.request.urlopen', autospec=True)
    def test_register_spam_check_fail(self, m_urlopen):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        a = Mock()
        a.read.side_effect = urllib.error.URLError("test url error")
        m_urlopen.return_value = a

        response = self.client.post(url, self.get_post_data(), follow=True)
        to_list = [admin[1] for admin in settings.ADMINS]
        assert_email_template_used(
            'Email Spam Check Error',
            settings.DEFAULT_FROM_EMAIL)
