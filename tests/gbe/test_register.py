from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_email_template_used,
    clear_conferences,
    grant_privilege,
    login_as,
)
from django_recaptcha.client import RecaptchaResponse
from mock import patch, Mock
import urllib
from django.core.files import File
from gbetext import found_on_list_msg
from django.conf import settings
from tests.contexts import StaffAreaContext
from datetime import (
    date,
    datetime,
)
from cms.test_utils.testcases import CMSTestCase
from cms.api import create_page


class TestRegister(CMSTestCase):
    '''Tests for register  view'''
    view_name = 'register'

    @classmethod
    def setUpTestData(cls):
        cls.counter = 0
        cls.page = create_page(
            "Welcome",
            "base.html",
            "en",
            published=True,
            overwrite_url="/")

    def get_post_data(self):
        self.counter += 1
        email = "new%d@last.com" % self.counter
        data = {'name': 'new last',
                'email': email,
                'password1': 'test',
                'password2': 'test',
                "g-recaptcha-response": "PASSED"}
        return data

    def check_subway_state(self, response, active_state="Create Account"):
        self.assertContains(
            response,
            '<li class="progressbar_active">%s</li>' % active_state,
            html=True)
        self.assertNotContains(
                response,
                '<li class="progressbar_upcoming">Payment</li>',
                html=True)

    def test_register_get(self):
        url = "%s?next=%s" % (
            reverse(self.view_name, urlconf='gbe.urls'),
            reverse('class_create', urlconf='gbe.urls'))

        response = self.client.get(url, follow=True)
        self.assertContains(response, "Create an Account")
        self.check_subway_state(response)

    @patch('urllib.request.urlopen', autospec=True)
    @patch("django_recaptcha.fields.client.submit")
    def test_register_post(self, mocked_submit, m_urlopen):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertRedirects(
            response,
            reverse('profile_update', urlconf='gbe.urls'))

    @patch('urllib.request.urlopen', autospec=True)
    @patch("django_recaptcha.fields.client.submit")
    def test_register_redirect(self, mocked_submit, m_urlopen):
        clear_conferences()
        conference = ConferenceFactory()
        save_the_date = datetime(2016, 2, 6, 12, 0, 0)
        day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 0o2, 0o6))
        self.staffcontext = StaffAreaContext(
            conference=conference,
            starttime=save_the_date)
        self.volunteeropp = self.staffcontext.add_volunteer_opp()
        url = "%s?next=%s" % (
            reverse(self.view_name, urlconf='gbe.urls'),
            reverse('volunteer_signup', urlconf='gbe.scheduling.urls'))

        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertRedirects(response, reverse(
            'volunteer_signup',
            urlconf='gbe.scheduling.urls'))

    def test_register_post_nothing(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        response = self.client.post(url, {'data': 'bad'}, follow=True)
        self.assertContains(response, "This field is required.")

    @patch("django_recaptcha.fields.client.submit")
    def test_register_unique_email(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        post_data = self.get_post_data()
        profile = ProfileFactory(user_object__email=post_data['email'])
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "That email address is already in use")

    @patch('urllib.request.urlopen', autospec=True)
    @patch("django_recaptcha.fields.client.submit")
    def test_register_spammer_email(self, mocked_submit, m_urlopen):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response_bad.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertContains(response, found_on_list_msg)

    @patch('urllib.request.urlopen', autospec=True)
    @patch("django_recaptcha.fields.client.submit")
    def test_register_spam_check_fail(self, mocked_submit, m_urlopen):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        a = Mock()
        a.read.side_effect = urllib.error.URLError("test url error")
        m_urlopen.return_value = a
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        response = self.client.post(url, self.get_post_data(), follow=True)
        to_list = [admin[1] for admin in settings.ADMINS]
        assert_email_template_used('Email Spam Check Error')
