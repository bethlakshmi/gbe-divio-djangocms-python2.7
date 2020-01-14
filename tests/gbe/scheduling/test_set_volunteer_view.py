from django.test import (
    TestCase,
    Client
)
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    EmailTemplateFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.contexts import (
    ClassContext,
    StaffAreaContext,
    VolunteerContext,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_email_recipient,
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
from settings import GBE_DATETIME_FORMAT


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
        self.unsub_link = Site.objects.get_current().domain + reverse(
            'profile_update',
            urlconf='gbe.urls'
            ) + "?email_disable=send_schedule_change_notifications"

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
        msg = assert_email_template_used(
            "A change has been made to your Volunteer Schedule!",
            outbox_size=2)
        assert("http://%s%s" % (
            Site.objects.get_current().domain,
            reverse('home', urlconf='gbe.urls')) in msg.body)
        assert_email_recipient([self.profile.user_object.email], outbox_size=2)
        staff_msg = assert_email_template_used(
            "Volunteer Schedule Change",
            outbox_size=2,
            message_index=1)
        assert(self.volunteeropp.eventitem.e_title in staff_msg.body)
        assert_email_recipient(
            [self.context.staff_lead.profile.user_object.email],
            outbox_size=2,
            message_index=1)

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
        msg = assert_email_template_used(
            "A change has been made to your Volunteer Schedule!",
            outbox_size=2)
        assert("http://%s%s" % (
            Site.objects.get_current().domain,
            reverse('home', urlconf='gbe.urls')) in msg.body)
        assert_email_recipient([self.profile.user_object.email], outbox_size=2)
        staff_msg = assert_email_template_used(
            "Volunteer Schedule Change",
            outbox_size=2,
            message_index=1)
        assert(self.volunteeropp.eventitem.e_title in staff_msg.body)
        assert_email_recipient(
            [self.context.staff_lead.profile.user_object.email],
            outbox_size=2,
            message_index=1)

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

    def test_volunteer_conflict(self):
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=PersonaFactory(performer_profile=self.profile),
            starttime=self.volunteeropp.starttime)
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf="gbe.urls")
        msg = assert_email_template_used(
            "A change has been made to your Volunteer Schedule!",
            outbox_size=2)
        assert("http://%s%s" % (
            Site.objects.get_current().domain,
            reverse('home', urlconf='gbe.urls')) in msg.body)
        assert_email_recipient([self.profile.user_object.email], outbox_size=2)
        staff_msg = assert_email_template_used(
            "Volunteer Schedule Change",
            outbox_size=2,
            message_index=1)
        assert(self.volunteeropp.eventitem.e_title in staff_msg.body)
        conflict_msg = 'Conflicting booking: %s, Start Time: %s' % (
            class_context.bid.e_title,
            class_context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT))
        assert(class_context.bid.e_title in staff_msg.body)
        assert_email_recipient(
            [self.privileged_user.email,
             self.context.staff_lead.profile.user_object.email],
            outbox_size=2,
            message_index=1)

    def test_parent_event(self):
        vol_context = VolunteerContext(
            conference=self.context.conference)
        lead = vol_context.set_staff_lead()
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=PersonaFactory(performer_profile=self.profile),
            starttime=vol_context.opp_event.starttime)
        url = reverse(
            self.view_name,
            args=[vol_context.opp_event.pk, "on"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.get(url, follow=True)
        staff_msg = assert_email_template_used(
            "Volunteer Schedule Change",
            outbox_size=2,
            message_index=1)
        assert(vol_context.opportunity.e_title in staff_msg.body)
        conflict_msg = 'Conflicting booking: %s, Start Time: %s' % (
            class_context.bid.e_title,
            class_context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT))
        assert(class_context.bid.e_title in staff_msg.body)
        assert_email_recipient(
            [lead.user_object.email],
            outbox_size=2,
            message_index=1)

    def test_email_fail(self):
        self.context.area.staff_lead = self.profile
        self.context.area.save()
        template = EmailTemplateFactory(
            name='volunteer changed schedule',
            content="{% include 'gbe/email/bad.tmpl' %}"
            )
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf="gbe.urls")
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, volunteer_allocate_email_fail_msg)
