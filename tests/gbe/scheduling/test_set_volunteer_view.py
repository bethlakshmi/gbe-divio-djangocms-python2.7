from django.test import (
    TestCase,
    Client
)
from django.contrib.sites.models import Site
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    EmailTemplateFactory,
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
from gbe.models import (
    Profile,
)
from gbetext import (
    no_login_msg,
    full_login_msg,
    paired_event_set_vol_msg,
    set_volunteer_msg,
    unset_volunteer_msg,
    set_pending_msg,
    unset_pending_msg,
    vol_opp_full_msg,
    vol_prof_update_failure,
    volunteer_allocate_email_fail_msg,
)
from gbe_utils.text import no_profile_msg
from settings import GBE_DATETIME_FORMAT
from datetime import datetime


class TestSetVolunteer(TestCase):
    view_name = "set_volunteer"

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory(phone="111-222-3333",
                                     user_object__first_name="Firstname",
                                     user_object__last_name="Lastname")
        cls.context = StaffAreaContext()

    def setUp(self):
        self.client = Client()
        self.volunteeropp = self.context.add_volunteer_opp()
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "on"],
            urlconf="gbe.scheduling.urls")
        self.unsub_link = Site.objects.get_current().domain + reverse(
            'email_update',
            urlconf='gbe.urls'
            ) + "?email_disable=send_schedule_change_notifications"

    def test_no_login_gives_error(self):
        response = self.client.post(self.url, follow=True)
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
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('profile_update',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Update Your Profile")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            no_profile_msg)

    def test_volunteer(self):
        login_as(self.profile, self)
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('volunteer_signup',
                               urlconf="gbe.scheduling.urls")
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.volunteeropp.title)
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
        assert(self.volunteeropp.title in staff_msg.body)
        assert_email_recipient(
            [self.context.staff_lead.user_object.email],
            outbox_size=2,
            message_index=1)

    def test_volunteer_for_full_linked_event(self):
        context = VolunteerContext()
        lead = context.set_staff_lead()
        link_opp = context.add_opportunity()
        link_opp.set_peer(context.opp_event)
        self.context.book_volunteer(
            volunteer_sched_event=context.opp_event)
        context.opp_event.max_volunteer = 1
        context.opp_event.save()
        login_as(self.profile, self)
        response = self.client.post(
            reverse(self.view_name,
                    args=[context.opp_event.pk, "on"],
                    urlconf="gbe.scheduling.urls"),
            follow=True)
        assert_alert_exists(
            response,
            'success',
            'Success',
            vol_opp_full_msg)

    def test_volunteer_for_linked_event(self):
        context = VolunteerContext()
        lead = context.set_staff_lead()
        link_opp = context.add_opportunity()
        link_opp.set_peer(context.opp_event)

        login_as(self.profile, self)
        response = self.client.post(
            reverse(self.view_name,
                    args=[context.opp_event.pk, "on"],
                    urlconf="gbe.scheduling.urls"),
            follow=True)
        redirect_url = reverse('volunteer_signup',
                               urlconf="gbe.scheduling.urls")
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, context.opp_event.title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            paired_event_set_vol_msg +
            context.opp_event.title + ', ' +
            link_opp.title)
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
        assert(context.opp_event.title in staff_msg.body)
        assert(link_opp.title in staff_msg.body)
        assert_email_recipient(
            [lead.user_object.email],
            outbox_size=2,
            message_index=1)

    def test_incomplete_volunteer_update(self):
        incomplete = ProfileFactory()
        login_as(incomplete, self)
        data = {'first_name': 'new first',
                'last_name': 'new last',
                'phone': '111-222-3333'}
        response = self.client.post(self.url,  data=data, follow=True)

        self.assertContains(response, self.volunteeropp.title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_volunteer_msg)
        now_complete = Profile.objects.get(pk=incomplete.pk)
        self.assertEqual(now_complete.user_object.first_name, "new first")
        self.assertEqual(now_complete.phone, "111-222-3333")

    def test_volunteer_update_fails(self):
        incomplete = ProfileFactory()
        login_as(incomplete, self)
        data = {'first_name': 'new first',
                'last_name': 'new last'}
        response = self.client.post(self.url,  data=data, follow=True)
        redirect_url = reverse('volunteer_signup',
                               urlconf="gbe.scheduling.urls")
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Phone")
        self.assertContains(response, self.volunteeropp.title)
        self.assertContains(response, vol_prof_update_failure)

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
        response = self.client.post("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.volunteeropp.title)
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
        assert(self.volunteeropp.title in staff_msg.body)
        assert_email_recipient(
            [self.context.staff_lead.user_object.email],
            outbox_size=2,
            message_index=1)

    def test_remove_linked_event_volunteer(self):
        context = VolunteerContext()
        lead = context.set_staff_lead()
        link_opp = context.add_opportunity()
        link_opp.set_peer(context.opp_event)
        self.url = reverse(
            self.view_name,
            args=[context.opp_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        # Shitty but effective
        self.context.book_volunteer(
            volunteer_sched_event=context.opp_event,
            volunteer=self.profile)
        self.context.book_volunteer(
            volunteer_sched_event=link_opp,
            volunteer=self.profile)
        redirect_url = reverse('volunteer_signup',
                               urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.post("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.volunteeropp.title)
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
        assert(context.opp_event.title in staff_msg.body)
        assert(link_opp.title in staff_msg.body)
        assert_email_recipient(
            [lead.user_object.email],
            outbox_size=2,
            message_index=1)

    def test_volunteer_duplicate(self):
        self.context.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile)
        redirect_url = reverse('home', urlconf="gbe.urls")
        login_as(self.profile, self)
        response = self.client.post("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, self.volunteeropp.title)
        self.assertNotContains(response, set_volunteer_msg)

    def test_remove_interest_duplicate(self):
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "off"],
            urlconf="gbe.scheduling.urls")
        redirect_url = reverse('home', urlconf="gbe.urls")
        login_as(self.profile, self)
        response = self.client.post("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        self.assertNotContains(response, self.volunteeropp.title)
        self.assertNotContains(response, unset_volunteer_msg)

    def test_show_interest_bad_event(self):
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk+100, "on"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.post(self.url, follow=True)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.volunteeropp.pk+100))

    def test_volunteer_needs_approval(self):
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        redirect_url = reverse('home', urlconf="gbe.urls")
        login_as(self.profile, self)
        response = self.client.post("%s?next=%s" % (
            self.url,
            redirect_url), follow=True)
        self.assertRedirects(response, redirect_url)
        # absent because pending events not on schedule to begin with
        self.assertNotContains(response, self.volunteeropp.title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_pending_msg)
        msg = assert_email_template_used(
            "Your volunteer proposal has changed status to awaiting approval",
            outbox_size=2)
        assert(self.volunteeropp.title in msg.body)

    def test_linked_event_needs_approval(self):
        context = VolunteerContext(conference=self.context.conference)
        self.volunteeropp.set_peer(context.opp_event)
        context.opp_event.approval_needed = True
        context.opp_event.starttime = datetime(2015, 2, 5)
        context.opp_event.save()
        redirect_url = reverse('home', urlconf="gbe.urls")
        login_as(self.profile, self)
        response = self.client.post("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        self.assertRedirects(response, redirect_url)
        # absent because pending events not on schedule to begin with
        self.assertNotContains(response, self.volunteeropp.title)
        self.assertNotContains(response, context.opp_event.title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_pending_msg)
        msg = assert_email_template_used(
            "Your volunteer proposal has changed status to awaiting approval",
            outbox_size=2)
        assert(self.volunteeropp.title in msg.body)

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
        response = self.client.post("%s?next=%s" % (
            self.url, redirect_url), follow=True)
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.volunteeropp.title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_pending_msg)
        msg = assert_email_template_used(
            "Your volunteer proposal has changed status to Withdrawn",
            outbox_size=2)
        assert(self.volunteeropp.title in msg.body)

    def test_remove_pending_volunteer_linked_event(self):
        context = VolunteerContext(conference=self.context.conference)
        self.volunteeropp.set_peer(context.opp_event)
        context.opp_event.approval_needed = True
        context.opp_event.starttime = datetime(2015, 2, 6)
        context.opp_event.save()
        self.context.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile,
            role="Pending Volunteer")
        self.context.book_volunteer(
            volunteer_sched_event=context.opp_event,
            volunteer=self.profile,
            role="Pending Volunteer")
        login_as(self.profile, self)
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "off"],
            urlconf="gbe.scheduling.urls")
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, self.volunteeropp.title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_pending_msg)
        msg = assert_email_template_used(
            "Your volunteer proposal has changed status to Withdrawn",
            outbox_size=2)
        assert(context.opp_event.title in msg.body)

    def test_remove_pending_volunteer_both_linked_event(self):
        context = VolunteerContext(conference=self.context.conference)
        self.volunteeropp.set_peer(context.opp_event)
        context.opp_event.approval_needed = True
        context.opp_event.starttime = datetime(2015, 2, 6)
        context.opp_event.save()
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        self.context.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile,
            role="Pending Volunteer")
        self.context.book_volunteer(
            volunteer_sched_event=context.opp_event,
            volunteer=self.profile,
            role="Pending Volunteer")
        login_as(self.profile, self)
        self.url = reverse(
            self.view_name,
            args=[self.volunteeropp.pk, "off"],
            urlconf="gbe.scheduling.urls")
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, self.volunteeropp.title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_pending_msg)
        msg = assert_email_template_used(
            "Your volunteer proposal has changed status to Withdrawn",
            outbox_size=2)
        assert(context.opp_event.title in msg.body)
        assert(self.volunteeropp.title in msg.body)

    def test_volunteer_conflict(self):
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=BioFactory(contact=self.profile),
            starttime=self.volunteeropp.starttime)
        login_as(self.profile, self)
        response = self.client.post(self.url, follow=True)
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
        assert(self.volunteeropp.title in staff_msg.body)
        conflict_msg = 'Conflicting booking: %s, Start Time: %s' % (
            class_context.bid.b_title,
            class_context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT))
        assert(class_context.bid.b_title in staff_msg.body)
        # even though there is a volunteer coordinator - mail only goes to
        # staff lead
        assert_email_recipient(
            [self.context.staff_lead.user_object.email],
            outbox_size=2,
            message_index=1)
        self.assertContains(response, conflict_msg)
        assert(conflict_msg in staff_msg.body)

    def test_parent_event(self):
        vol_context = VolunteerContext(
            conference=self.context.conference)
        lead = vol_context.set_staff_lead()
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=BioFactory(contact=self.profile),
            starttime=vol_context.opp_event.starttime)
        url = reverse(
            self.view_name,
            args=[vol_context.opp_event.pk, "on"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.post(url, follow=True)
        staff_msg = assert_email_template_used(
            "Volunteer Schedule Change",
            outbox_size=2,
            message_index=1)
        assert(vol_context.opp_event.title in staff_msg.body)
        conflict_msg = 'Conflicting booking: %s, Start Time: %s' % (
            class_context.bid.b_title,
            class_context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT))
        assert(class_context.bid.b_title in staff_msg.body)
        assert_email_recipient(
            [lead.user_object.email],
            outbox_size=2,
            message_index=1)
        self.assertContains(response, conflict_msg)
        assert(conflict_msg in staff_msg.body)

    def test_mail_vol_coordinator_when_no_lead(self):
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        vol_context = VolunteerContext(
            conference=self.context.conference)
        url = reverse(
            self.view_name,
            args=[vol_context.opp_event.pk, "on"],
            urlconf="gbe.scheduling.urls")
        login_as(self.profile, self)
        response = self.client.post(url, follow=True)
        assert_email_recipient(
            [self.privileged_user.email],
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
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('volunteer_signup',
                               urlconf="gbe.scheduling.urls")
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, volunteer_allocate_email_fail_msg)
