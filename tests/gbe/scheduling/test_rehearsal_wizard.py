from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
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


class TestRehearsalWizard(TestScheduling):
    '''Tests for the 2nd stage in the rehearsal wizard view'''
    view_name = 'rehearsal_wizard'

    def setUp(self):
        self.show_volunteer = VolunteerContext()
        self.current_conference = self.show_volunteer.conference
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "rehearsal")
        self.assertContains(response, self.show_volunteer.sched_event.title)
        self.assertContains(response,
                            "Make New Show")

    def test_authorized_user_empty_conference(self):
        other_conf = ConferenceFactory()
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[other_conf.conference_slug],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url)
        self.assertNotContains(response, self.show_volunteer.sched_event.title)
        self.assertContains(response,
                            "Make New Show")

    def test_auth_user_can_pick_show(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_show': True,
                'show': self.show_volunteer.sched_event.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?rehearsal_open=True" % reverse(
                'edit_show',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      self.show_volunteer.sched_event.pk]))

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_show': True,
                'show': "boo"})
        self.assertContains(
            response,
            'Select a valid choice. boo is not one of the available choices.')

    def test_auth_user_pick_new_show(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_show': True,
                'show': ""},
            follow=True)
        self.assertRedirects(
            response,
            reverse('create_ticketed_event_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug,
                          "show"])+"?")
