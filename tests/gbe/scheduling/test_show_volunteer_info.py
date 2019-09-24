from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import ResourceAllocationFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.functions.scheduler_functions import (
    assert_link,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
    VolunteerContext,
)
from gbe.models import AvailableInterest
from datetime import timedelta
'''
#
#  This is a spin off of edit volunteers.
#    It's the testing for the case of presenting eligible volunteers on an
#    event that is a volunteer opportunity.  Not testing the basics, as they
#    are covered elsewhere (ie, privileges and basic bad data)
#
'''


class TestShowVolunteers(TestCase):
    view_name = 'edit_volunteer'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.context = VolunteerContext()
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.opp_event.pk],
            urlconf="gbe.scheduling.urls")

    def test_no_available_volunteers(self):
        context = StaffAreaContext()
        volunteer_opp = context.add_volunteer_opp()
        volunteer, alloc = context.book_volunteer(
            volunteer_opp)
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(
                self.view_name,
                args=[context.conference.conference_slug,
                      volunteer_opp.pk],
                urlconf="gbe.scheduling.urls"),
            follow=True)
        assert ("no available volunteers" in response.content)

    def test_volunteer_has_conflict(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert("no available volunteers" not in response.content)
        assert_link(response, self.url)

    def test_volunteer_has_class_conflict(self):
        class_context = ClassContext(
            conference=self.context.conference,
            teacher=PersonaFactory(performer_profile=self.context.profile),
            starttime=self.context.opp_event.start_time)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert("no available volunteers" not in response.content)
        assert_link(response, reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  class_context.sched_event.pk],
            urlconf="gbe.scheduling.urls"))

    def test_volunteer_has_show_conflict(self):
        show_context = ShowContext(
            conference=self.context.conference,
            performer=PersonaFactory(performer_profile=self.context.profile),
            starttime=self.context.opp_event.start_time)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert("no available volunteers" not in response.content)
        assert_link(response, reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  show_context.sched_event.pk],
            urlconf="gbe.scheduling.urls"))

    def test_volunteer_has_earlier_conflict(self):
        opportunity, opp_event = self.context.add_opportunity(
            start_time=self.context.opp_event.start_time-timedelta(minutes=30))
        conflict = ResourceAllocationFactory(resource=self.context.worker,
                                             event=opp_event)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert("no available volunteers" not in response.content)
        assert_link(response, reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  opp_event.pk],
            urlconf="gbe.scheduling.urls"))

    def test_volunteer_is_available(self):
        self.context.bid.available_windows.add(self.context.window)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert ("no available volunteers" not in response.content)
        assert('<td class="bid-table">Available</td>' in response.content)

    def test_volunteer_is_not_available(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert ("no available volunteers" not in response.content)
        assert('<td class="bid-table">Not Available</td>' in response.content)

    def test_volunteer_is_really_not_available(self):
        self.context.bid.unavailable_windows.add(self.context.window)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert ("no available volunteers" in response.content)

    def test_volunteer_is_interested(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert('4 - Somewhat interested' in response.content)

    def test_volunteer_is_not(self):
        self.context.interest.rank = 0
        self.context.interest.save()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert('4 - Somewhat interested' not in response.content)
        assert("no available volunteers" not in response.content)

    def test_volunteer_has_no_rank(self):
        self.context.interest.delete()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        assert('4 - Somewhat interested' not in response.content)
        assert("no available volunteers" not in response.content)
