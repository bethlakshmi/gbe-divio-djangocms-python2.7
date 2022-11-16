from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from settings import (
    GBE_DATE_FORMAT,
    GBE_DATETIME_FORMAT,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from datetime import timedelta
from tests.gbe.test_gbe import TestGBE


class TestEditVolunteer(TestGBE):
    view_name = 'edit_volunteer'

    def setUp(self):
        self.context = VolunteerContext(event=GenericEventFactory())
        self.context.sched_event.max_volunteer = 7
        self.context.sched_event.save()
        self.context.event.duration = timedelta(hours=1, minutes=30)
        self.context.event.save()
        self.room = self.context.room
        self.staff_lead = self.context.set_staff_lead()
        self.extra_day = ConferenceDayFactory(
            conference=self.context.conference,
            day=self.context.conf_day.day + timedelta(days=1))
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.opp_event.pk],
            urlconf='gbe.scheduling.urls')
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def edit_event(self):
        data = {
            'approval': True,
            'type': 'Volunteer',
            'e_title': "Test Event Wizard",
            'slug': "EditVolSlug",
            'e_description': 'Description',
            'max_volunteer': 3,
            'parent_event': '',
            'staff_area': '',
            'day': self.extra_day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'set_event': 'Any value',
        }
        return data

    def test_not_volunteer_redirect(self):
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse('edit_event',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug,
                          self.context.sched_event.pk]) + "?")

    def test_authorized_user_can_access_event_w_parent(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Manage Volunteers")
        self.assertContains(response, "Finish")
        self.assertContains(response, self.context.opportunity.e_title)
        self.assertContains(response, self.context.opportunity.e_description)
        self.assertContains(
            response,
            '<option value="%d" selected>%s - %s</option>' % (
                self.context.sched_event.pk,
                self.context.event.e_title,
                self.context.sched_event.start_time.strftime(
                    GBE_DATETIME_FORMAT)),
            html=True)
        assert_option_state(
            response,
            self.context.conf_day.pk,
            self.context.conf_day.day.strftime(GBE_DATE_FORMAT),
            True)

    def test_authorized_user_can_also_get_volunteer_mgmt(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteer Allocation")
        self.assertContains(response, "Save and Continue")
        self.assertContains(
            response,
            '<option value="" selected>---------</option>')
        self.assert_hidden_value(
            response,
            "id_alloc_id",
            "alloc_id",
            -1)

    def test_vol_is_booked(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assert_hidden_value(
            response,
            "id_alloc_id",
            "alloc_id",
            self.context.allocation.pk)
        assert_option_state(
            response,
            self.context.profile.pk,
            self.context.profile.display_name,
            True)
        self.assertContains(
            response,
            '<option value="Volunteer" selected>Volunteer</option>',
            2)

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

    def test_edit_event(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
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
                self.context.opp_event.pk))
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
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['e_title'])

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
            "%s?worker_open=True" % self.url)
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
        self.assertContains(response, data['slug'])
        assert_option_state(
            response,
            self.extra_day.pk,
            self.extra_day.day.strftime(GBE_DATE_FORMAT),
            True)
        self.assertContains(
            response,
            '<input type="number" name="max_volunteer" value="3" min="0" ' +
            'required id="id_max_volunteer">',
            html=True)
        self.assertContains(
            response,
            '<input type="number" name="duration" value="2.5" min="0.5" ' +
            'max="12" step="any" required id="id_duration" />',
            html=True)
        self.assertContains(
            response,
            '<input type="checkbox" name="approval" ' +
            'id="id_approval" checked />',
            html=True)
        self.assertContains(
            response,
            '<option value="%d">%s - %s</option>' % (
                self.context.sched_event.pk,
                self.context.event.e_title,
                self.context.sched_event.start_time.strftime(
                    GBE_DATETIME_FORMAT)),
            html=True)

    def test_edit_event_change_parent(self):
        other_context = VolunteerContext(conference=self.context.conference)
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['parent_event'] = other_context.sched_event.pk
        data['edit_event'] = "Save and Continue"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?worker_open=True" % self.url)
        self.assertContains(
            response,
            '<option value="%d" selected>%s - %s</option>' % (
                other_context.sched_event.pk,
                other_context.event.e_title,
                other_context.sched_event.start_time.strftime(
                    GBE_DATETIME_FORMAT)),
            html=True)

    def test_edit_event_set_area(self):
        other_context = StaffAreaContext(conference=self.context.conference)
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['staff_area'] = other_context.area.pk
        data['edit_event'] = "Save and Continue"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?worker_open=True" % self.url)
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                other_context.area.pk,
                other_context.area),
            html=True)

    def test_edit_event_unset_area(self):
        staff_context = StaffAreaContext()
        volunteer_sched_event = staff_context.add_volunteer_opp()
        volunteer_sched_event.approval_needed = True
        volunteer_sched_event.save()
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[staff_context.conference.conference_slug,
                            volunteer_sched_event.pk])
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['edit_event'] = "Save and Continue"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (
                staff_context.area.pk,
                staff_context.area),
            html=True)

    def test_auth_user_bad_schedule_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['location'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")

    def test_post_bad_occurrence(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.opp_event.pk+1000],
            urlconf='gbe.scheduling.urls')
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.opp_event.pk+1000))

    def test_good_user_get_volunteer_w_teacher_as_persona(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        staff_context = StaffAreaContext()
        volunteer_sched_event = staff_context.add_volunteer_opp()
        volunteer_sched_event.approval_needed = True
        volunteer_sched_event.save()
        teacher = PersonaFactory()
        teacher, alloc = staff_context.book_volunteer(
            volunteer_sched_event=volunteer_sched_event,
            volunteer=teacher,
            role="Teacher")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[staff_context.conference.conference_slug,
                            volunteer_sched_event.pk])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<input type="checkbox" name="approval" ' +
            'id="id_approval" checked />',
            html=True)

        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                staff_context.area.pk,
                staff_context.area),
            html=True)

    def test_inactive_user_not_listed(self):
        staff_context = StaffAreaContext()
        volunteer_sched_event = staff_context.add_volunteer_opp()
        inactive_persona = PersonaFactory(
            contact__user_object__is_active=False)
        login_as(self.privileged_user, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[staff_context.conference.conference_slug,
                            volunteer_sched_event.pk])
        response = self.client.get(url)
        self.assertNotContains(response, str(inactive_persona))
        self.assertNotContains(response, str(inactive_persona.contact))
