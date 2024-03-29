from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ConferenceDayFactory,
    RoomFactory,
    ProfileFactory,
)
from scheduler.models import (
    Event,
    Ordering,
    PeopleAllocation,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from settings import GBE_DATE_FORMAT
from tests.contexts import (
    ClassContext,
    ShowContext,
    VolunteerContext,
)
from datetime import timedelta
from tests.gbe.scheduling.test_scheduling import TestScheduling


class TestEditEventView(TestScheduling):
    '''This view edits classes that were made through the wizard'''
    view_name = 'edit_event'

    def setUp(self):
        self.context = VolunteerContext(event_style="Special")
        self.context.sched_event.max_volunteer = 7
        self.context.sched_event.length = timedelta(hours=1, minutes=30)
        self.context.sched_event.save()
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
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def edit_event(self):
        data = {
            'type': 'Special',
            'title': "Test Event Wizard",
            'slug': "EditSlug",
            'description': 'Description',
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
        self.assert_role_choice(response, "Staff Lead")
        self.assertNotContains(response, "Volunteer Management")
        self.assertContains(response, "Finish")
        self.assertContains(response, self.context.sched_event.title)
        self.assertContains(response, self.context.sched_event.description)
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
        slot = self.context.make_rehearsal()
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  slot.pk],
            urlconf='gbe.scheduling.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Finish")
        self.assertContains(response, slot.title)
        self.assertNotContains(response, 'Display Staff')

    def test_vol_opp_present(self):
        vol_context = VolunteerContext()
        vol_context.sched_event.max_volunteer = 7
        vol_context.sched_event.save()
        vol_context.opp_event.set_locations([])
        vol_context.opp_event.length = timedelta(hours=7, minutes=30)
        vol_context.opp_event.save()
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
            '<input type="number" name="duration" value="7.5" min="0.25" ' +
            'max="12" step="any" required id="id_duration">',
            html=True)

    def test_edit_class(self):
        class_context = ClassContext()
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[class_context.conference.conference_slug,
                  class_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse(
            "edit_class",
            args=[class_context.conference.conference_slug,
                  class_context.sched_event.pk],
            urlconf='gbe.scheduling.urls'))

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
                data['title'],
                self.extra_day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['title'])
        # staff lead should be created, without order.  If order is created,
        # landing page will fail to fetch act with 500 error.
        prof = self.privileged_user.profile.__class__.__name__
        self.assertTrue(PeopleAllocation.objects.filter(
            people__class_id=self.privileged_user.profile.pk,
            people__class_name=prof,
            people__commitment_class_id__isnull=True,
            event=self.context.sched_event,
            role=data['alloc_0-role']
            ).exists())
        self.assertFalse(Ordering.objects.filter(
            people_allocated__people__class_id=self.privileged_user.profile.pk,
            people_allocated__people__class_name=prof,
            people_allocated__people__commitment_class_id__isnull=True,
            people_allocated__event=self.context.sched_event,
            people_allocated__role=data['alloc_0-role']
            ).exists())

    def test_edit_event_without_staffing(self):
        login_as(self.privileged_user, self)
        show_context = ShowContext(conference=self.context.conference)
        slot = show_context.make_rehearsal()
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  slot.pk],
            urlconf='gbe.scheduling.urls')
        data = self.edit_event()
        del(data['alloc_0-role'])
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
                slot.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['title'],
                self.extra_day.day.strftime(GBE_DATE_FORMAT))
            )

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
        data['title'] = ""
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
