from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.formats import date_format
from tests.factories.gbe_factories import (
    ActFactory,
    EmailTemplateFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import (
    LabelFactory,
    OrderingFactory,
    ResourceAllocationFactory,
    WorkerFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_email_recipient,
    assert_email_template_used,
    grant_privilege,
    login_as,
)
from tests.contexts import (
    ClassContext,
    StaffAreaContext,
    VolunteerContext,
)
from gbe.models import (
    Conference,
    Profile,
)
from scheduler.models import ResourceAllocation
from settings import (
    GBE_DATETIME_FORMAT,
    GBE_TABLE_FORMAT,
)
from gbetext import (
    set_volunteer_role_msg,
    volunteer_allocate_email_fail_msg,
)
from django.contrib.sites.models import Site
from django.db.models import Max
from datetime import timedelta


class TestApproveVolunteer(TestCase):
    '''Tests for review_volunteer view'''
    view_name = 'review_pending'
    approve_name = 'approve_volunteer'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        Conference.objects.all().delete()
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Volunteer Coordinator')
        cls.context = VolunteerContext()
        cls.url = reverse(cls.view_name, urlconf='gbe.scheduling.urls')

    def assert_volunteer_state(self, response, booking, disabled_action=""):
        self.assertContains(response,
                            str(booking.resource.worker._item.profile))
        self.assertContains(response, str(booking.event))
        self.assertContains(
            response,
            booking.event.start_time.strftime(GBE_TABLE_FORMAT))
        self.assertContains(
            response,
            booking.event.end_time.strftime(GBE_TABLE_FORMAT))
        for action in ['approve', 'reject', 'waitlist']:
            if action == disabled_action:
                self.assertContains(
                    response,
                    '<a href="None" class="btn gbe-btn-table gbe-btn-xs ' +
                    'disabled" data-toggle="tooltip" title="%s">' % (
                        action.capitalize()))
            else:
                self.assertContains(response, reverse(
                    self.approve_name,
                    urlconf='gbe.scheduling.urls',
                    args=[action,
                          booking.resource.worker._item.profile.pk,
                          booking.pk]))

    def test_list_volunteers_bad_user(self):
        ''' user does not have Volunteer Coordinator, permission is denied'''
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(403, response.status_code)

    def test_list_volunteer_no_volunteers(self):
        '''default conference selected, make sure it returns the right page'''
        '''Acts that are waitlisted do not show up'''
        waitlisted_act = ActFactory(b_conference=self.context.conference,
                                    accepted=2,
                                    submitted=True)
        booking = ResourceAllocationFactory(
            event=self.context.sched_event,
            resource=WorkerFactory(_item=waitlisted_act.performer,
                                   role="Waitlisted"))
        order = OrderingFactory(
            allocation=booking,
            class_id=waitlisted_act.pk,
            class_name="Act",
            role="Waitlisted")
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approve Pending Volunteers')
        self.assertNotContains(response, self.context.sched_event.title)
        self.assertNotContains(response, waitlisted_act.performer.name)

    def test_list_volunteer_w_conf(self):
        ''' check conference selector, no data is in table.'''
        second_context = VolunteerContext()
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            {'conf_slug': second_context.conference.conference_slug})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approve Pending Volunteers')
        self.assertContains(
            response,
            '<option value = "%s" selected>' % (
                second_context.conference.conference_slug))
        self.assertContains(
            response,
            '<option value = "%s">' % (
                self.context.conference.conference_slug))

    def test_list_volunteer_as_staff_lead(self):
        self.context.worker.role = "Pending Volunteer"
        label = LabelFactory(allocation=self.context.allocation)
        self.context.worker.save()
        staff_context = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staff_context.book_volunteer(
            role="Pending Volunteer")

        login_as(staff_context.staff_lead, self)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approve Pending Volunteers')
        self.assertNotContains(
            response,
            'Select conference',
            msg_prefix="Staff Lead should not get conference picker")

        # lead can get their own volunteers
        response = self.client.get(
            self.url,
            {'conf_slug': self.context.conference.conference_slug})
        self.assert_volunteer_state(response, booking)
        self.assertContains(response, str(staff_context.area))

        # ... but not anyone else's
        self.assertNotContains(
            response,
            str(self.context.allocation.resource.worker._item.profile))
        self.assertNotContains(
            response,
            str(self.context.allocation.event))

    def test_get_pending(self):
        self.context.worker.role = "Pending Volunteer"
        label = LabelFactory(allocation=self.context.allocation)
        self.context.worker.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(response, self.context.allocation)
        self.assertContains(response, str(self.context.sched_event))
        self.assertContains(response,
                            '<tr class="gbe-table-row gbe-table-info">')
        self.assertContains(response, label.text)

    def test_get_inactive_user(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        self.context.profile.user_object.is_active = False
        self.context.profile.user_object.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(response, self.context.allocation)
        self.assertContains(response,
                            '<tr class="gbe-table-row gbe-table-danger">')

    def test_event_full(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        self.context.opp_event.max_volunteer = 0
        self.context.opp_event.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(response, self.context.allocation)
        self.assertContains(response, str(self.context.sched_event))
        self.assertContains(response,
                            '<tr class="gbe-table-row gbe-table-warning">')

    def test_set_waitlist(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["waitlist",
                  self.context.profile.pk,
                  self.context.allocation.pk]))
        self.assert_volunteer_state(
            response,
            self.context.allocation,
            "waitlist")
        self.assertContains(response,
                            '<tr class="gbe-table-row gbe-table-success">')
        alert_msg = set_volunteer_role_msg % "Waitlisted"
        full_msg = '%s Person: %s<br/>Event: %s, Start Time: %s' % (
                alert_msg,
                str(self.context.profile),
                str(self.context.opp_event),
                self.context.opp_event.starttime.strftime(
                    GBE_DATETIME_FORMAT))
        assert_alert_exists(
            response,
            'success',
            'Success',
            full_msg)
        assert_email_template_used(
            "Your volunteer proposal has changed status to Wait List",
            outbox_size=2)

    def test_redirects(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        response = self.client.get("%s?next=%s" % (
            reverse(self.approve_name,
                    urlconf='gbe.scheduling.urls',
                    args=["waitlist",
                          self.context.profile.pk,
                          self.context.allocation.pk]),
            reverse("home", urlconf='gbe.urls')), follow=True)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))

    def test_set_reject(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["reject",
                  self.context.profile.pk,
                  self.context.allocation.pk]))
        self.assert_volunteer_state(
            response,
            self.context.allocation,
            "reject")
        self.assertContains(response,
                            '<tr class="gbe-table-row gbe-table-success">')
        alert_msg = set_volunteer_role_msg % "Rejected"
        full_msg = '%s Person: %s<br/>Event: %s, Start Time: %s' % (
                alert_msg,
                str(self.context.profile),
                str(self.context.opp_event),
                self.context.opp_event.starttime.strftime(
                    GBE_DATETIME_FORMAT))
        assert_alert_exists(
            response,
            'success',
            'Success',
            full_msg)
        assert_email_template_used(
            "Your volunteer proposal has changed status to Reject",
            outbox_size=2)

    def test_approve(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  self.context.profile.pk,
                  self.context.allocation.pk])
        response = self.client.get(approve_url)
        self.assertNotContains(response, approve_url)
        self.assertNotContains(response,
                               '<tr class="gbe-table-row gbe-table-success">')
        alert_msg = set_volunteer_role_msg % "Volunteer"
        full_msg = '%s Person: %s<br/>Event: %s, Start Time: %s' % (
                alert_msg,
                str(self.context.profile),
                str(self.context.opp_event),
                self.context.opp_event.starttime.strftime(
                    GBE_DATETIME_FORMAT))
        assert_alert_exists(
            response,
            'success',
            'Success',
            full_msg)
        msg = assert_email_template_used(
            "A change has been made to your Volunteer Schedule!",
            outbox_size=2)
        assert("http://%s%s" % (
            Site.objects.get_current().domain,
            reverse('home', urlconf='gbe.urls')) in msg.body)
        assert_email_recipient([self.context.profile.user_object.email],
                               outbox_size=2)
        staff_msg = assert_email_template_used(
            "Volunteer Schedule Change",
            outbox_size=2,
            message_index=1)
        assert(str(self.context.opp_event) in staff_msg.body)
        assert_email_recipient(
            [self.privileged_user.email],
            outbox_size=2,
            message_index=1)

    def test_approval_w_conflict(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=PersonaFactory(performer_profile=self.context.profile),
            starttime=self.context.opp_event.starttime)
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  self.context.profile.pk,
                  self.context.allocation.pk])
        response = self.client.get(approve_url)
        self.assertNotContains(response, approve_url)
        self.assertNotContains(response,
                               '<tr gbe-table-row gbe-table-success">')
        conflict_msg = 'Conflicting booking: %s, Start Time: %s' % (
            class_context.bid.b_title,
            class_context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT))
        self.assertContains(response, conflict_msg)

        staff_msg = assert_email_template_used(
            "Volunteer Schedule Change",
            outbox_size=2,
            message_index=1)
        assert(conflict_msg in staff_msg.body)
        assert(class_context.bid.b_title in staff_msg.body)
        assert_email_recipient(
            [self.privileged_user.email],
            outbox_size=2,
            message_index=1)

    def test_approval_w_conflict_start_after(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=PersonaFactory(performer_profile=self.context.profile),
            starttime=self.context.opp_event.starttime + timedelta(minutes=30))
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  self.context.profile.pk,
                  self.context.allocation.pk])
        response = self.client.get(approve_url)
        self.assertNotContains(response, approve_url)
        conflict_msg = 'Conflicting booking: %s, Start Time: %s' % (
            class_context.bid.b_title,
            class_context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT))
        self.assertContains(response, conflict_msg)

    def test_approval_w_conflict_start_before(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=PersonaFactory(performer_profile=self.context.profile),
            starttime=self.context.opp_event.starttime - timedelta(minutes=30))
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  self.context.profile.pk,
                  self.context.allocation.pk])
        response = self.client.get(approve_url)
        self.assertNotContains(response, approve_url)
        conflict_msg = 'Conflicting booking: %s, Start Time: %s' % (
            class_context.bid.b_title,
            class_context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT))
        self.assertContains(response, conflict_msg)

    def test_staff_lead_approval(self):
        staff_context = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staff_context.book_volunteer(
            role="Pending Volunteer")
        login_as(staff_context.staff_lead, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  volunteer.pk,
                  booking.pk])
        response = self.client.get(approve_url)
        alert_msg = set_volunteer_role_msg % "Volunteer"
        full_msg = '%s Person: %s<br/>Event: %s, Start Time: %s' % (
                alert_msg,
                str(volunteer),
                str(booking.event),
                booking.event.starttime.strftime(
                    GBE_DATETIME_FORMAT))
        assert_alert_exists(
            response,
            'success',
            'Success',
            full_msg)

    def test_staff_lead_fail_out_of_scope(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        staff_context = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staff_context.book_volunteer(
            role="Pending Volunteer")
        login_as(staff_context.staff_lead, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  self.context.profile.pk,
                  self.context.allocation.pk])
        response = self.client.get(approve_url)
        self.assertEqual(403, response.status_code)

    def test_set_bad_id(self):
        staff_context = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staff_context.book_volunteer(
            role="Pending Volunteer")
        login_as(staff_context.staff_lead, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  volunteer.pk,
                  booking.pk+100])
        response = self.client.get(approve_url)
        self.assertEqual(404, response.status_code)

    def test_stage_manager_approve(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        stage_mgr = self.context.set_staff_lead(role="Stage Manager")
        login_as(stage_mgr, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  self.context.profile.pk,
                  self.context.allocation.pk])
        response = self.client.get("%s?next=%s" % (
            approve_url,
            reverse('home', urlconf='gbe.urls')), follow=True)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        alert_msg = set_volunteer_role_msg % "Volunteer"
        full_msg = '%s Person: %s<br/>Event: %s, Start Time: %s' % (
                alert_msg,
                str(self.context.profile),
                str(self.context.opp_event),
                self.context.opp_event.starttime.strftime(
                    GBE_DATETIME_FORMAT))
        assert_alert_exists(
            response,
            'success',
            'Success',
            full_msg)

    def test_stage_manager_fail_out_of_scope(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        stage_mgr = self.context.set_staff_lead(role="Stage Manager")
        staff_context = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staff_context.book_volunteer(
            role="Pending Volunteer")
        login_as(stage_mgr, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  volunteer.pk,
                  booking.pk])
        response = self.client.get("%s?next=%s" % (
            approve_url,
            reverse('home', urlconf='gbe.urls')))
        self.assertEqual(403, response.status_code)

    def test_stage_manager_list_fail(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        stage_mgr = self.context.set_staff_lead(role="Stage Manager")
        login_as(stage_mgr, self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_email_fail(self):
        template = EmailTemplateFactory(
            name='volunteer changed schedule',
            content="{% include 'gbe/email/bad.tmpl' %}"
            )
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        approve_url = reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["approve",
                  self.context.profile.pk,
                  self.context.allocation.pk])
        response = self.client.get(approve_url)
        self.assertContains(response, volunteer_allocate_email_fail_msg)

    def test_set_bad_booking(self):
        bad_id = ResourceAllocation.objects.aggregate(Max('pk'))['pk__max']+1
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.approve_name,
            urlconf='gbe.scheduling.urls',
            args=["waitlist", self.context.profile.pk, bad_id]))
        self.assertContains(response, "Booking id %s not found" % bad_id)

    def test_approve_volunteers_bad_volunteer(self):
        ''' user does not have Volunteer Coordinator, permission is denied'''
        bad_id = Profile.objects.aggregate(Max('pk'))['pk__max']+1
        login_as(self.privileged_user, self)
        response = self.client.get(
            reverse(
                self.approve_name,
                urlconf='gbe.scheduling.urls',
                args=["waitlist", bad_id, self.context.allocation.pk]),
            follow=True)
        self.assertEqual(404, response.status_code)
