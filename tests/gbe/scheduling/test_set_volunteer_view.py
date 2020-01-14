from django.test import (
    TestCase,
    Client
)
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.contexts import StaffAreaContext
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_email_template_used,
    grant_privilege,
    login_as,
)
from django.shortcuts import get_object_or_404
from gbe.models import Volunteer
from gbetext import (
    no_profile_msg,
    no_login_msg,
    full_login_msg,
    set_volunteer_msg,
    unset_volunteer_msg,
    set_pending_msg,
    unset_pending_msg,
    volunteer_allocate_email_fail_msg,
)


class TestSetFavorite(TestCase):
    view_name = "set_volunteer"

    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()
        self.context = StaffAreaContext()
        self.volunteeropp = self.context.add_volunteer_opp()
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "on"],
            urlconf="gbe.scheduling.urls")

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            full_login_msg % (no_login_msg, reverse(
                'login',
                urlconf='gbe.urls') + "?next=" + self.url))

    def test_unfinished_user(self):
        unfinished = UserFactory()
        login_as(unfinished, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            no_profile_msg)

    def test_volunteer(self):
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf="gbe.urls")
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.volunteeropp.eventitem.e_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_volunteer_msg)

    def test_remove_volunteer(self):
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.context.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile)
        redirect_url = reverse('volunteer_signup', 
                               urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.get("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.volunteeropp.eventitem.e_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_volunteer_msg)

    def test_volunteer_duplicate(self):
        self.context.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile)
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, self.volunteeropp.eventitem.e_title)
        self.assertNotContains(response, set_volunteer_msg)

    def test_remove_interest_duplicate(self):
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "off"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)
        self.assertNotContains(response, unset_volunteer_msg)

    def test_show_interest_bad_event(self):
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk+100, "on"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.volunteeropp.pk+100))

    def test_volunteer_needs_approval(self):
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf="gbe.urls")
        self.assertRedirects(response, redirect_url)
        # absent because pending events not on schedule to begin with
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_pending_msg)

    def test_remove_pending_volunteer(self):
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.context.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile,
            role="Pending Volunteer")
        redirect_url = reverse('volunteer_signup', 
                               urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.get("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.volunteeropp.eventitem.e_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_pending_msg)
