from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import timedelta
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
    setup_admin_w_privs,
)
from gbe.models import (
    ConferenceDay,
)
from tests.contexts import VolunteerContext
from gbetext import (
    change_day_note,
    missing_day_form_note,
)


class TestManageConference(TestCase):
    view_name = 'manage_conference'

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs(['Admins'])
        cls.profile = cls.privileged_user.profile
        cls.day = ConferenceDayFactory()
        cls.url = reverse(cls.view_name, urlconf="gbe.scheduling.urls")

    def setUp(self):
        self.client = Client()

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('login') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_not_admin(self):
        not_admin = ProfileFactory()
        grant_privilege(not_admin, 'Admins')
        login_as(not_admin, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.day.conference.conference_slug)
        self.assertContains(
            response,
            ('<input type="text" name="%d-day" id="id_%d_day" ' +
             'class="form-control  datetimepicker-input" ' +
             'data-toggle="datetimepicker" data-target="#id_%d_day">') % (
             self.day.pk, self.day.pk, self.day.pk),
            html=True)

    def test_get_conf_no_days(self):
        no_days = ConferenceFactory(status="upcoming")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.day.conference.conference_slug)
        self.assertNotContains(response, no_days.conference_slug)
        self.assertContains(
            response,
            ('<input type="text" name="%d-day" id="id_%d_day" ' +
             'class="form-control  datetimepicker-input" ' +
             'data-toggle="datetimepicker" data-target="#id_%d_day">') % (
             self.day.pk, self.day.pk, self.day.pk),
            html=True)

    def test_post_bad_day(self):
        login_as(self.profile, self)
        response = self.client.post(
            reverse("schedule_conference",
                    urlconf="gbe.scheduling.urls",
                    args=[self.day.pk+1]),
            data={'%d-day' % self.day.pk: self.day.day+timedelta(days=30)},
            follow=True)
        self.assertEqual(response.status_code, 404)

    def test_post_no_day(self):
        login_as(self.profile, self)
        response = self.client.post(
            self.url,
            data={'%d-day' % self.day.pk: self.day.day+timedelta(days=30)},
            follow=True)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_form(self):
        login_as(self.profile, self)
        response = self.client.post(
            reverse("schedule_conference",
                    urlconf="gbe.scheduling.urls",
                    args=[self.day.pk]),
            data={'%d-day' % self.day.pk: "bad day"},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid date.")

    def test_post_missing_day(self):
        login_as(self.profile, self)
        response = self.client.post(
            reverse("schedule_conference",
                    urlconf="gbe.scheduling.urls",
                    args=[self.day.pk]),
            data={'day': self.day.day+timedelta(days=30)},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_post(self):
        login_as(self.profile, self)
        response = self.client.post(
            reverse("schedule_conference",
                    urlconf="gbe.scheduling.urls",
                    args=[self.day.pk]),
            data={'%d-day' % self.day.pk: self.day.day+timedelta(days=30)},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            ("%s?%s-calendar_type=0&%s-calendar_type=1&%s-calendar_type=2" +
             "&filter=Filter") % (
             reverse('manage_event_list', urlconf='gbe.scheduling.urls'),
             self.day.conference.conference_slug,
             self.day.conference.conference_slug,
             self.day.conference.conference_slug))
        self.assertContains(
            response,
            "Moved Conference %s by %d days, change %d conference days" % (
                self.day.conference.conference_slug,
                30,
                1))
        self.assertContains(
            response,
            "Moved %d scheduled events by %d days" % (
                0,
                30))

    def test_post_event_change(self):
        VolunteerContext(conference=self.day.conference)
        login_as(self.profile, self)
        response = self.client.post(
            reverse("schedule_conference",
                    urlconf="gbe.scheduling.urls",
                    args=[self.day.pk]),
            data={'%d-day' % self.day.pk: self.day.day+timedelta(days=30)},
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            ("%s?%s-calendar_type=0&%s-calendar_type=1&%s-calendar_type=2" +
             "&filter=Filter") % (
             reverse('manage_event_list', urlconf='gbe.scheduling.urls'),
             self.day.conference.conference_slug,
             self.day.conference.conference_slug,
             self.day.conference.conference_slug))
        self.assertContains(
            response,
            "Moved Conference %s by %d days, change %d conference days" % (
                self.day.conference.conference_slug,
                30,
                1))
        self.assertContains(
            response,
            "Moved %d scheduled events by %d days" % (
                2,
                30))

    def test_post_no_form_for_day(self):
        login_as(self.profile, self)
        self.day.conference.status = 'completed'
        self.day.conference.save()
        response = self.client.post(
            reverse("schedule_conference",
                    urlconf="gbe.scheduling.urls",
                    args=[self.day.pk]),
            data={'%d-day' % self.day.pk: self.day.day+timedelta(days=30)})
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            change_day_note)
        self.assertContains(
            response,
            missing_day_form_note)
