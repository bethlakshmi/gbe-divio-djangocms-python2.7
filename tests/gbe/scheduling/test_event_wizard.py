from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe_forms_text import event_type_options


class TestEventWizard(TestCase):
    '''Tests for the first stage in the event wizard view'''
    view_name = 'create_event_wizard'

    def setUp(self):
        self.current_conference = ConferenceFactory(accepting_bids=True)
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def get_data(self, event_type='conference'):
        data = {
            'event_type': event_type,
            'pick_event': 'Next'
        }
        return data

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response,
                               "panel-collapse collapse")
        for header in event_type_options:
            self.assertContains(response, header[0])
            for subitem in header[1]:
                self.assertContains(response, subitem[1])

    def test_auth_user_can_pick_conf_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.get(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(response, "%s?event_type=%s&pick_event=Next" % (
            reverse('create_class_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug]),
            data['event_type']))

    def test_auth_user_can_pick_master_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data("master")
        response = self.client.get(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(response, "%s?event_type=%s&pick_event=Next" % (
            reverse('create_ticketed_event_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug,
                          data['event_type']]),
            data['event_type']))

    def test_auth_user_can_pick_dropin_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data("drop-in")
        response = self.client.get(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(response, "%s?event_type=%s&pick_event=Next" % (
            reverse('create_ticketed_event_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug,
                          data['event_type']]),
            data['event_type']))

    def test_auth_user_can_pick_staff(self):
        login_as(self.privileged_user, self)
        data = self.get_data("staff")
        response = self.client.get(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(response, "%s?event_type=%s&pick_event=Next" % (
            reverse('staff_area_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug]),
            data['event_type']))

    def test_auth_user_can_pick_volunteer(self):
        login_as(self.privileged_user, self)
        data = self.get_data("volunteer")
        response = self.client.get(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(response, "%s?event_type=%s&pick_event=Next" % (
            reverse('create_volunteer_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug]),
            data['event_type']))

    def test_auth_user_can_pick_rehearsal(self):
        login_as(self.privileged_user, self)
        data = self.get_data("rehearsal")
        response = self.client.get(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(response, "%s?event_type=%s&pick_event=Next" % (
            reverse('rehearsal_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug]),
            data['event_type']))

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        data['event_type'] = 123
        response = self.client.get(
            self.url,
            data=data)
        self.assertContains(
            response,
            'Select a valid choice. 123 is not one of the available choices.')
