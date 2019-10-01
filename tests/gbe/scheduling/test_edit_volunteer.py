from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
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
from tests.functions.gbe_scheduling_functions import (
    assert_good_sched_event_form_wizard,
)
from settings import GBE_DATE_FORMAT
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from gbe.duration import Duration
from datetime import timedelta


class TestEditVolunteer(TestCase):
    view_name = 'edit_volunteer'

    def setUp(self):
        self.context = VolunteerContext(event=GenericEventFactory())
        self.context.sched_event.max_volunteer = 7
        self.context.sched_event.save()
        self.context.event.duration = Duration(hours=1, minutes=30)
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
            'type': 'Volunteer',
            'e_title': "Test Event Wizard",
            'e_description': 'Description',
            'max_volunteer': 3,
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

    def test_authorized_user_can_access_event(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Manage Volunteers")
        self.assertContains(response, "Finish")
        self.assertContains(response, self.context.opportunity.e_title)
        self.assertContains(response, self.context.opportunity.e_description)
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
        self.assertContains(
            response,
            'type="hidden" name="alloc_id" value="-1" id="id_alloc_id" />')

    def test_vol_is_booked(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            'type="hidden" name="alloc_id" value="%d" id="id_alloc_id" />' % (
                self.context.allocation.pk))
        assert_option_state(
            response,
            self.context.profile.pk,
            self.context.profile.display_name,
            True)
        self.assertContains(
            response,
            '<option value="Volunteer" selected>Volunteer</option>',
            3)

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
        assert_option_state(
            response,
            self.extra_day.pk,
            self.extra_day.day.strftime(GBE_DATE_FORMAT),
            True)
        self.assertContains(
            response,
            'name="max_volunteer" value="3" required id="id_max_volunteer" />')
        self.assertContains(
            response,
            'name="duration" value="2.5" max="12" step="any" ' +
            'required id="id_duration" min="0.5" />')

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
        self.assertNotIn(str(inactive_persona), response.content)
        self.assertNotIn(str(inactive_persona.contact), response.content)
