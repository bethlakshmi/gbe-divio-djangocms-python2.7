from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ProfileFactory,
)
from tests.contexts import ClassContext
from django.urls import reverse
from tests.functions.gbe_functions import (
    clear_conferences,
    login_as,
    setup_social_media
)


class TestBiosTeachers(TestCase):
    '''Tests for bios_teachers view'''
    view_name = 'bios_teacher'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.conference = ConferenceFactory(status='upcoming',
                                           accepting_bids=True)
        cls.url = reverse(cls.view_name, urlconf="gbe.urls")

    def test_bios_teachers_no_active_conf(self):
        clear_conferences()
        other_conference = ConferenceFactory(status="completed")
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_bios_teachers_no_conf_slug(self):
        current_context = ClassContext(conference=self.conference)
        other_conference = ConferenceFactory(status="completed")
        other_context = ClassContext(conference=other_conference)
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, current_context.teacher.name)
        self.assertContains(response, current_context.bid.b_title)
        self.assertNotContains(response, other_context.teacher.name)
        self.assertNotContains(response, other_context.bid.b_title)

    def test_bios_teachers_specific_conference(self):
        first_context = ClassContext()
        link = first_context.set_social_media("Facebook")
        other_context = ClassContext()
        login_as(ProfileFactory(), self)
        response = self.client.get(
            self.url,
            data={'conference': first_context.conference.conference_slug})
        assert response.status_code == 200
        self.assertContains(response, first_context.bid.teacher.name)
        self.assertContains(response, first_context.bid.b_title)
        self.assertContains(response, setup_social_media(link))
        self.assertNotContains(response, other_context.bid.teacher.name)
        self.assertNotContains(response, other_context.bid.b_title)

    def test_bios_teachers_unbooked_accepted(self):
        accepted_class = ClassFactory(b_conference=self.conference,
                                      accepted=3)
        login_as(ProfileFactory(), self)
        response = self.client.get(
            self.url,
            data={'conference': accepted_class.b_conference.conference_slug})

        assert response.status_code == 200
        self.assertContains(response, accepted_class.teacher.name)
        self.assertContains(response, accepted_class.b_title)

    def test_bios_teachers_profile_skipped(self):
        first_context = ClassContext()
        first_context.people.class_id = first_context.teacher.contact.pk
        first_context.people.class_name = "Profile"
        first_context.people.save()
        login_as(ProfileFactory(), self)
        response = self.client.get(
            self.url,
            data={'conference': first_context.conference.conference_slug})
        assert response.status_code == 200
        self.assertNotContains(response, first_context.bid.teacher.name)
        self.assertNotContains(response, first_context.bid.b_title)
        self.assertNotContains(response,
                               first_context.teacher.contact.display_name)
