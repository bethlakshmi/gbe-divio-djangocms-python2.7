from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
    RoomFactory,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from scheduler.models import Event
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from settings import GBE_DATE_FORMAT
from tests.gbe.scheduling.test_scheduling import TestScheduling


class TestVolunteerWizard(TestScheduling):
    '''Tests for the 2nd and 3rd stage in the volunteer wizard view'''
    view_name = 'create_volunteer_wizard'

    @classmethod
    def setUpTestData(cls):
        cls.room = RoomFactory()
        cls.show_volunteer = VolunteerContext()
        cls.current_conference = cls.show_volunteer.conference
        cls.room.conferences.add(cls.current_conference)
        cls.special_volunteer = VolunteerContext(
            event_style="Special",
            conference=cls.current_conference)
        cls.staff_area = StaffAreaContext(
            conference=cls.current_conference)
        cls.url = reverse(
            cls.view_name,
            args=[cls.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Scheduling Mavens')

    def create_opp(self):
        data = {
            'type': 'Volunteer',
            'conference': self.current_conference.pk,
            'title': "Test Volunteer Wizard #%d" % self.room.pk,
            'slug': "VolunteerSlug",
            'description': 'Description',
            'max_volunteer': 0,
            'day': self.special_volunteer.conf_day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'approval': True,
            'location': self.room.pk,
            'alloc_0-role': 'Staff Lead',
            'alloc_0-worker': self.staff_area.staff_lead.pk,
            'set_opp': 'Finish',
        }
        return data

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "volunteer")
        self.assertContains(response,
                            str(self.show_volunteer.sched_event.title))
        self.assertContains(response,
                            str(self.special_volunteer.sched_event.title))
        self.assertContains(response, str(self.staff_area.area.title))
        self.assertContains(response,
                            "Make a Volunteer Opportunity with no topic")

    def test_authorized_user_empty_conference(self):
        other_conf = ConferenceFactory()
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[other_conf.conference_slug],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url)
        self.assertNotContains(response,
                               str(self.show_volunteer.sched_event.title))
        self.assertNotContains(response,
                               str(self.special_volunteer.sched_event.title))
        self.assertNotContains(response, str(self.staff_area.area.title))
        self.assertContains(response,
                            "Make a Volunteer Opportunity with no topic")

    def test_auth_user_can_pick_show(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': self.show_volunteer.sched_event.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?volunteer_open=True" % reverse(
                'edit_show',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      self.show_volunteer.sched_event.pk]))

    def test_auth_user_can_pick_special(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': self.special_volunteer.sched_event.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?volunteer_open=True" % reverse(
                'edit_event',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      self.special_volunteer.sched_event.pk]))

    def test_auth_user_can_pick_staff(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': "staff_%d" % self.staff_area.area.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?volunteer_open=True" % reverse(
                'edit_staff',
                urlconf='gbe.scheduling.urls',
                args=[self.staff_area.area.pk]))

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': "boo"})
        self.assertContains(
            response,
            'Select a valid choice. boo is not one of the available choices.')

    def test_auth_user_pick_new_opp(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': ""},
            follow=True)
        self.assert_radio_state(response,
                                "volunteer_topic",
                                "id_volunteer_topic_3_0",
                                "",
                                True)
        self.assertContains(
            response,
            'Make New Volunteer Opportunity')
        self.assertContains(
            response,
            '<input type="checkbox" name="approval" id="id_approval" />',
            html=True)

    def test_auth_user_create_opp(self):
        login_as(self.privileged_user, self)
        data = self.create_opp()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.order_by('pk').last()
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.special_volunteer.conf_day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['title'],
                self.special_volunteer.conf_day.day.strftime(
                    GBE_DATE_FORMAT)))
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['title'])
        self.assertTrue(occurrence.approval_needed)
        self.assertEqual(occurrence.slug, "VolunteerSlug")

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.create_opp()
        data['alloc_0-role'] = "bad role"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "bad role is not one of the available choices.")

    def test_auth_user_bad_schedule_assign(self):
        login_as(self.privileged_user, self)
        data = self.create_opp()
        data['location'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")

    def test_auth_user_bad_booking_assign(self):
        login_as(self.privileged_user, self)
        data = self.create_opp()
        data['title'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")
