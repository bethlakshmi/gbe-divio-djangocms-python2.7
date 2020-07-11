from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    GenericEventFactory,
    RoomFactory,
    ProfileFactory,
)
from scheduler.models import Event
from gbe.models import (
    GenericEvent,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from tests.functions.gbe_scheduling_functions import (
    assert_event_was_picked_in_wizard,
    assert_good_sched_event_form_wizard,
    assert_role_choice,
)
from settings import GBE_DATE_FORMAT
from tests.contexts import (
    ShowContext,
    VolunteerContext,
)
from datetime import timedelta


class TestEditEventView(TestCase):
    '''This view edits classes that were made through the wizard'''
    view_name = 'edit_event'

    def setUp(self):
        self.context = VolunteerContext(event=GenericEventFactory())
        self.context.sched_event.max_volunteer = 7
        self.context.sched_event.save()
        self.context.event.duration = timedelta(hours=1, minutes=30)
        self.context.event.save()
        self.room = self.context.room
        # because there was a bug around duplicate room names
        RoomFactory(name=self.room.name)
        self.staff_lead = self.context.set_staff_lead()
        self.extra_day = ConferenceDayFactory(
            conference=self.context.conference,
            day=self.context.conf_day.day + timedelta(days=1))
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def edit_event(self):
        data = {
            'type': 'Special',
            'e_title': "Test Event Wizard",
            'e_description': 'Description',
            'max_volunteer': 3,
            'day': self.extra_day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'set_event': 'Any value',
            'alloc_0-role': 'Staff Lead',
        }
        return data

    def test_edit_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access_event(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assert_role_choice(response, "Staff Lead")
        self.assertNotContains(response, "Volunteer Management")
        self.assertContains(response, "Finish")
        self.assertContains(response, self.context.event.e_title)
        self.assertContains(response, self.context.event.e_description)
        assert_option_state(
            response,
            self.context.conf_day.pk,
            self.context.conf_day.day.strftime(GBE_DATE_FORMAT),
            True)
        self.assertContains(response,
                            'name="max_volunteer" value="7"')
        self.assertContains(
            response,
            'name="duration" value="1.5"')
        assert_option_state(response,
                            self.staff_lead.pk,
                            str(self.staff_lead),
                            True)

    def test_authorized_user_can_also_get_volunteer_mgmt(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteer Management")
        self.assertContains(response, "Save and Continue")
        assert_option_state(response,
                            self.context.conf_day.pk,
                            self.context.conf_day.day.strftime("%b. %-d, %Y"),
                            True)
        self.assertContains(
            response,
            'name="new_opp-max_volunteer" value="7"')
        self.assertContains(
            response,
            'name="new_opp-duration" value="1.5"')

    def test_authorized_user_can_access_rehearsal(self):
        self.context = ShowContext()
        rehearsal, slot = self.context.make_rehearsal()
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  slot.pk],
            urlconf='gbe.scheduling.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Finish")
        self.assertContains(response, rehearsal.e_title)
        self.assertNotContains(response, 'Display Staff')

    def test_vol_opp_present(self):
        vol_context = VolunteerContext()
        vol_context.sched_event.max_volunteer = 7
        vol_context.sched_event.save()
        vol_context.opp_event.set_locations([])
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[vol_context.conference.conference_slug,
                  vol_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            'type="hidden" name="opp_event_id" value="%d"' % (
                vol_context.opportunity.pk)
        )
        self.assertContains(
            response,
            'type="hidden" name="opp_sched_id" value="%d"' % (
                vol_context.opp_event.pk)
        )
        assert_option_state(response,
                            vol_context.conf_day.pk,
                            vol_context.conf_day.day.strftime("%b. %-d, %Y"),
                            True)
        self.assertContains(
            response,
            'name="max_volunteer" value="2"')
        self.assertContains(
            response,
            'name="duration" value="1.0"')
        self.assertContains(response, "Display Staff", 2)

    def test_bad_conference(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=["BadConf",
                  self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_bad_occurrence_id(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk+1000],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1000))

    def test_edit_event_w_staffing(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['alloc_0-worker'] = self.privileged_user.profile.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug]),
                self.context.conference.conference_slug,
                self.extra_day.pk,
                self.context.sched_event.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.extra_day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

    def test_edit_event_and_continue(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['edit_event'] = "Save and Continue"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?volunteer_open=True" % self.url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.extra_day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(response, data['e_title'])
        self.assertContains(response, data['e_description'])
        assert_option_state(response,
                            self.extra_day.pk,
                            self.extra_day.day.strftime(GBE_DATE_FORMAT),
                            True)
        self.assertContains(response,
                            'name="max_volunteer" value="3"')
        self.assertContains(
            response,
            'name="duration" value="2.5"')

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['alloc_0-role'] = "bad role"
        data['alloc_1-role'] = "bad role"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "bad role is not one of the available choices.")

    def test_auth_user_bad_schedule_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['location'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")

    def test_auth_user_bad_room_assign(self):
        not_this_room = RoomFactory()
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['location'] = not_this_room.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "That choice is not one of the available choices.")

    def test_auth_user_bad_generic_booking_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['e_title'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "This field is required.")

    def test_post_bad_occurrence(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk+1000],
            urlconf='gbe.scheduling.urls')
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1000))
