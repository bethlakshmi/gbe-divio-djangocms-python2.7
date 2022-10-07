from django.test import TestCase
from django.test import Client
from django.urls import reverse
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
from mock import patch, Mock
import urllib
from django.core.files import File
from gbetext import (
    email_in_use_msg,
    found_on_list_msg,
)
from django.conf import settings


class TestEditProfile(TestCase):
    '''Tests for update_profile  view'''
    view_name = 'profile_update'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.counter = 0
        self.profile = ProfilePreferencesFactory().profile

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
                'show_hotel_infobox': False,
                'email_pref-send_daily_schedule': True,
                'email_pref-send_bid_notifications': False,
                'email_pref-send_role_notifications': False,
                'email_pref-send_schedule_change_notifications': True, }
        if invalid:
            del(data['first_name'])
        return data

    def post_profile(self, redirect=None, form=None):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        if redirect:
            url = url + "?next=" + redirect
        login_as(self.profile, self)
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
        self.assertContains(
            response,
            "%s %s" % (
                pref.profile.user_object.first_name,
                pref.profile.user_object.last_name))

    def test_update_profile_no_preferences(self):
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile.user_object, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            "Email Options")

    def test_update_profile_how_heard(self):
        pref = ProfilePreferencesFactory(
            profile__how_heard="[u'Word of mouth']")
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(pref.profile.user_object, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            '<input type="checkbox" name="how_heard" value="Word of mouth" ' +
            'id="id_how_heard_6" checked />',
            html=True)

    def test_update_profile_email_settings(self):
        pref = ProfilePreferencesFactory(
            send_bid_notifications=False)
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(pref.profile.user_object, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            '<input type="checkbox" name="email_pref-send_daily_schedule" ' +
            'id="id_email_pref-send_daily_schedule" checked />',
            html=True)
        self.assertContains(
            response,
            '<input type="checkbox" name="email_pref-send_bid_notifications"' +
            ' id="id_email_pref-send_bid_notifications" />',
            html=True)
        self.assertContains(response, email_pref_note.replace("'", "&#x27;"))

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_post_empty_display_name(self, m_urlopen):
        data = self.get_form()
        data['display_name'] = ""
        data['purchase_email'] = ""
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.post_profile(form=data)
        self.assertContains(
            response,
            "%s %s" % (data['first_name'].title(),
                       data['last_name'].title()))

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_post_cleanup_display_name(self, m_urlopen):
        data = self.get_form()
        data['display_name'] = " trim me   nocaps"
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.post_profile(form=data)
        self.assertContains(response, "Trim Me Nocaps")

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_post_valid_form(self, m_urlopen):
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.post_profile()
        self.assertContains(response, "Dashboard")
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        preferences = ProfilePreferences.objects.get(profile=self.profile)
        self.assertTrue(preferences.send_daily_schedule)
        self.assertFalse(preferences.send_bid_notifications)

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_post_valid_form_keep_email(self, m_urlopen):
        self.profile.email = "TheCaseDoesntMatter@email.com"
        self.profile.save()
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_form()
        data['email'] = "thecasedoesntmatter@email.com"
        login_as(self.profile, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))

    def test_update_profile_post_duplicate_email(self):
        self.other_profile = ProfileFactory(
            user_object__email="TheCaseDoesntMatter@email.com")

        url = reverse(self.view_name, urlconf='gbe.urls')
        data = self.get_form()
        data['email'] = "thecasedoesntmatter@email.com"
        login_as(self.profile, self)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, email_in_use_msg)

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_post_valid_redirect(self, m_urlopen):
        context = VolunteerContext()
        context.conference.accepting_bids = True
        context.conference.save()
        redirect = reverse('volunteer_signup', urlconf='gbe.scheduling.urls')
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.post_profile(redirect=redirect)
        self.assertRedirects(response, redirect)

    def test_update_profile_post_invalid_form(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        data = self.get_form(invalid=True)
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, "Your Profile")
        self.assertEqual(response.status_code, 200)

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_make_message(self, m_urlopen):
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.post_profile()
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_has_message(self, m_urlopen):
        msg = UserMessageFactory(
            view='EditProfileView',
            code='UPDATE_PROFILE')
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.post_profile()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    @patch('urllib.request.urlopen', autospec=True)
    def test_update_profile_bad_email(self, m_urlopen):
        a = Mock()
        ok_email_filename = open("tests/gbe/forum_spam_response_bad.xml", 'r')
        a.read.side_effect = [File(ok_email_filename).read()]
        m_urlopen.return_value = a

        response = self.post_profile()
        self.assertContains(response, found_on_list_msg)
