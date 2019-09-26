from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
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
    assert_radio_state,
    grant_privilege,
    login_as,
)
from tests.functions.gbe_scheduling_functions import (
    assert_event_was_picked_in_wizard,
    assert_good_sched_event_form_wizard,
)
from settings import GBE_DATE_FORMAT


class TestVolunteerWizard(TestCase):
    '''Tests for the 2nd and 3rd stage in the volunteer wizard view'''
    view_name = 'create_volunteer_wizard'

    def setUp(self):
        self.room = RoomFactory()
        self.show_volunteer = VolunteerContext()
        self.current_conference = self.show_volunteer.conference
        self.special_volunteer = VolunteerContext(
            event=GenericEventFactory(
                e_conference=self.current_conference))
        self.staff_area = StaffAreaContext(
            conference=self.current_conference)
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def create_opp(self):
        data = {
            'type': 'Volunteer',
            'e_conference': self.current_conference.pk,
            'e_title': "Test Volunteer Wizard #%d" % self.room.pk,
            'e_description': 'Description',
            'max_volunteer': 0,
            'day': self.special_volunteer.window.day.pk,
            'time': '11:00:00',
            'duration': 2.5,
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
        assert_event_was_picked_in_wizard(response, "volunteer")
        self.assertContains(response, str(self.show_volunteer.event.e_title))
        self.assertContains(response,
                            str(self.special_volunteer.event.e_title))
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
                               str(self.show_volunteer.event.e_title))
        self.assertNotContains(response,
                               str(self.special_volunteer.event.e_title))
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
        assert_radio_state(response, 
                           "volunteer_topic", 
                           "id_volunteer_topic_3_0", 
                           "", 
                           True)
        self.assertContains(
            response,
            'Make New Volunteer Opportunity')

    def test_auth_user_create_opp(self):
        login_as(self.privileged_user, self)
        data = self.create_opp()
        data['eventitem_id'] = ""
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
                self.special_volunteer.window.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.special_volunteer.window.day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

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
        data['e_title'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")
