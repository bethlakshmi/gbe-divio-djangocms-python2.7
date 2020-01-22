from django.test import TestCase
from django.test import Client
from django.core.exceptions import PermissionDenied
from datetime import datetime, date, time
from django.core.urlresolvers import reverse
from django.utils.formats import date_format
import pytz
import re
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    VolunteerContext,
    StaffAreaContext
)
from gbe.models import Conference
from django.utils.formats import date_format


class TestApproveVolunteer(TestCase):
    '''Tests for review_volunteer view'''
    view_name = 'review_pending'
    approve_name = 'approve_volunteer'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        self.context = VolunteerContext()
        self.url = reverse(self.view_name, urlconf='gbe.scheduling.urls')

    def assert_volunteer_state(self, response, booking, disabled_action=""):
        self.assertContains(response, 
                            str(booking.resource.worker._item.profile))
        self.assertContains(response, str(booking.event))
        self.assertContains(
            response, 
            date_format(booking.event.start_time, "SHORT_DATETIME_FORMAT"))
        self.assertContains(
            response, 
            date_format(booking.event.end_time, "SHORT_DATETIME_FORMAT"))
        for action in ['approve', 'reject', 'waitlist']:
            if action == disabled_action:
                self.assertContains(
                    response,
                    '<a href="None" class="btn btn-default btn-xs disabled" ' +
                    'data-toggle="tooltip" title="%s">' % action.capitalize())
            else:
                self.assertContains(response, reverse(
                    self.approve_name,
                    urlconf='gbe.scheduling.urls',
                    args=[action, booking.pk]))

    def test_approve_volunteers_bad_user(self):
        ''' user does not have Volunteer Coordinator, permission is denied'''
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(403, response.status_code)

    def test_approve_volunteer_no_volunteers(self):
        '''default conference selected, make sure it returns the right page'''
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approve Pending Volunteers')

    def test_approve_volunteer_w_conf(self):
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

    def test_approve_volunteer_as_staff_lead(self):
        staff_context = StaffAreaContext()

        login_as(staff_context.staff_lead, self)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approve Pending Volunteers')

    def test_get_pending(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(response, self.context.allocation)
        self.assertContains(response, str(self.context.sched_event))
        self.assertContains(response, '<tr class="bid-table info">')

    def test_get_waitlist(self):
        self.context.worker.role = "Waitlisted"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(
            response,
            self.context.allocation,
            "waitlist")

    def test_get_rejected(self):
        self.context.worker.role = "Rejected"
        self.context.worker.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(
            response,
            self.context.allocation,
            "reject")

    def test_get_staff_area(self):
        staff_context = StaffAreaContext(conference=self.context.conference)
        volunteer, booking = staff_context.book_volunteer(
            role="Pending Volunteer")
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            {'conf_slug': self.context.conference.conference_slug})
        self.assert_volunteer_state(response, booking)
        self.assertContains(response, str(staff_context.area))

    def test_get_inactive_user(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        self.context.profile.user_object.is_active = False
        self.context.profile.user_object.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(response, self.context.allocation)
        self.assertContains(response, '<tr class="bid-table danger">')

    def test_event_full(self):
        self.context.worker.role = "Pending Volunteer"
        self.context.worker.save()
        self.context.opp_event.max_volunteer = 0
        self.context.opp_event.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_volunteer_state(response, self.context.allocation)
        self.assertContains(response, str(self.context.sched_event))
        self.assertContains(response, '<tr class="bid-table warning">')
