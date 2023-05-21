from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ProfileFactory,
)
from tests.contexts import ClassContext
from gbe.models import (
    Conference
)
from django.urls import reverse
from tests.functions.gbe_functions import (
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

    def test_bios_teachers_no_conf_slug(self):
        current_context = ClassContext(conference=self.conference)
        other_conference = ConferenceFactory(status="completed")
        other_context = ClassContext(conference=other_conference)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, current_context.teacher.name)
        self.assertContains(response, current_context.bid.b_title)
        self.assertNotContains(response, other_context.teacher.name)
        self.assertNotContains(response, other_context.bid.b_title)

    def test_bios_teachers_specific_conference(self):
        first_context = ClassContext()
        link = first_context.set_social_media("Facebook")
        other_context = ClassContext()
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(
            url,
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
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(
            url,
            data={'conference': accepted_class.b_conference.conference_slug})

        assert response.status_code == 200
        self.assertContains(response, accepted_class.teacher.name)
        self.assertContains(response, accepted_class.b_title)
