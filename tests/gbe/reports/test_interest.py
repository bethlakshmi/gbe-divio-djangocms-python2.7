from django.urls import reverse
from django.test import TestCase
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.contexts import ClassContext
from gbe.models import Conference
from gbetext import interested_report_explain_msg


class TestInterest(TestCase):
    view_name = "interest"

    @classmethod
    def setUpTestData(cls):
        cls.priv_profile = ProfileFactory()
        cls.context = ClassContext()
        cls.old_conference = ConferenceFactory(status="completed")
        cls.old_context = ClassContext(conference=cls.old_conference)
        grant_privilege(cls.priv_profile, 'Class Coordinator')
        cls.url = reverse(cls.view_name, urlconf="gbe.reporting.urls")

    def test_interest_not_visible_without_permission(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_default_conf_success(self):
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.bid.b_title)
        self.assertNotContains(response, self.old_context.bid.b_title)
        self.assertContains(response, self.context.teacher.name)
        self.assertNotContains(response, self.old_context.teacher.name)
        self.assertContains(response, self.context.room.name)
        self.assertNotContains(response, self.old_context.room.name)

    def test_interest_is_present(self):
        interested = []
        for i in range(0, 3):
            interested += [self.context.set_interest()]
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for person in interested:
            self.assertContains(
                response,
                "%s &lt;%s&gt;;" % (person.display_name,
                                    person.user_object.email))

    def test_interest_old_conf(self):
        interested = []
        for i in range(0, 3):
            interested += [self.old_context.set_interest()]
        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.old_context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        for person in interested:
            self.assertContains(
                response,
                "%s &lt;%s&gt;;" % (person.display_name,
                                    person.user_object.email))

    def test_info_is_present(self):
        interested = []
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            interested_report_explain_msg)
