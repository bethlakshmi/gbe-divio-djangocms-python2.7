from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.factories.scheduler_factories import PeopleAllocationFactory
from tests.contexts import ClassContext
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
)
from tests.functions.scheduler_functions import get_or_create_profile
from django.shortcuts import get_object_or_404
from gbe.models import Volunteer
from gbe_utils.text import no_profile_msg
from gbetext import (
    no_login_msg,
    full_login_msg,
    set_favorite_msg,
    unset_favorite_msg,
)


class TestSetFavorite(TestCase):
    view_name = "set_favorite"

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory()
        cls.people = get_or_create_profile(cls.profile)
        cls.context = ClassContext()
        cls.url = reverse(
            cls.view_name,
            args=[cls.context.sched_event.pk, "on"],
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
            full_login_msg % (no_login_msg,
                              reverse('login') + "?next=" + self.url))

    def test_unfinished_user(self):
        unfinished = UserFactory()
        login_as(unfinished, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('profile_update',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Update Your Profile")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            no_profile_msg)

    def test_show_interest(self):
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.context.bid.b_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_favorite_msg)

    def test_remove_interest(self):
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        PeopleAllocationFactory(event=self.context.sched_event,
                                people=self.people,
                                role="Interested")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertNotContains(response, self.context.bid.b_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_favorite_msg)

    def test_show_interest_duplicate(self):
        PeopleAllocationFactory(event=self.context.sched_event,
                                people=self.people,
                                role="Interested")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.context.bid.b_title)
        self.assertNotContains(response, set_favorite_msg)

    def test_remove_interest_duplicate(self):
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertNotContains(response, self.context.bid.b_title)
        self.assertNotContains(response, unset_favorite_msg)

    def test_show_interest_bad_event(self):
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk+100, "on"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+100))

    def test_show_interest_redirect(self):
        login_as(self.profile, self)
        redirect_url = reverse(
            'detail_view',
            args=[self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get("%s?next=%s" % (self.url, redirect_url),
                                   follow=True)
        self.assertRedirects(response, redirect_url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_favorite_msg)

    def test_show_interest_also_volunteer(self):
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        booking = PeopleAllocationFactory(
            event=self.context.sched_event,
            people=self.people,
            role="Interested",
            label="label text")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertNotContains(response, self.context.bid.b_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_favorite_msg)
