from django.test import TestCase
import json
from django.urls import reverse
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from tests.factories.gbe_factories import ProfileFactory


class TestPersonaAutoComplete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory.create().user_object
        grant_privilege(cls.privileged_user,
                        'Scheduling Mavens',
                        'view_event')
        cls.staffcontext = StaffAreaContext()
        cls.volunteeropp = cls.staffcontext.add_volunteer_opp()
        cls.differentopp = cls.staffcontext.add_volunteer_opp()
        cls.differentopp.title = "TOTALLY DIFFERENT"
        cls.differentopp.save()
        cls.url = reverse('volunteer-autocomplete',
                          urlconf="gbe.scheduling.urls")

    def test_no_query(self):
        login_as(self.privileged_user, self)
        response = self.client.get("%s" % self.url)
        self.assertContains(response, self.volunteeropp.title)
        self.assertContains(response, self.volunteeropp.pk)
        self.assertContains(response, self.differentopp.title)

    def test_no_login(self):
        response = self.client.get("%s" % self.url, follow=True)
        self.assertRedirects(response, "%s?next=%s" % (
            reverse("login"),
            self.url))
        self.assertNotContains(response, self.volunteeropp.title)

    def test_first_three(self):
        login_as(self.privileged_user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            self.volunteeropp.title[:3]))
        self.assertContains(response, self.volunteeropp.title)
        self.assertContains(response, self.volunteeropp.pk)
        self.assertNotContains(response, self.differentopp.title)

    def test_limit_conference(self):
        otherconfarea = StaffAreaContext()
        otheropp = otherconfarea.add_volunteer_opp()
        login_as(self.privileged_user, self)
        response = self.client.get("%s?forward=%s" % (
            self.url,
            json.dumps({
                'label': self.staffcontext.conference.conference_slug, })))
        self.assertContains(response, self.volunteeropp.title)
        self.assertNotContains(response, otheropp.title)

    def test_parent_search(self):
        volcontext = VolunteerContext(conference=self.staffcontext.conference)
        volcontext.sched_event.title = "SHOW FOR AUTOCOMPLETE"
        volcontext.sched_event.save()
        login_as(self.privileged_user, self)
        response = self.client.get("%s?q=%s" % (
            self.url,
            volcontext.sched_event.title))
        self.assertContains(response, "%s - %s" % (
            volcontext.sched_event.title,
            volcontext.opp_event.title))
        self.assertNotContains(response, self.volunteeropp.title)
