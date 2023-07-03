from django.urls import reverse
from datetime import timedelta
from django.test import TestCase, Client
from gbe.models import Conference
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    ConferenceFactory,
    ProfileFactory,
)
from tests.contexts import ClassContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import space_options


class TestRoomSchedule(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory()

    def test_room_schedule_fail(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        current_conference = ConferenceFactory()
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_schedule',
                    urlconf='gbe.reporting.urls'),
            follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_room_schedule_succeed(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        context = ClassContext()
        one_day = timedelta(1)
        ConferenceDayFactory(conference=context.conference,
                             day=context.sched_event.starttime.date())
        ConferenceDayFactory(
            conference=context.conference,
            day=context.sched_event.starttime.date()+one_day)
        context.schedule_instance(
            starttime=context.sched_event.starttime + one_day)
        current_conference = context.conference
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_schedule',
                    urlconf='gbe.reporting.urls'))
        self.assertContains(response, context.room.name)
        self.assertContains(response, context.bid.b_title, 2)
        self.assertContains(response, "Teacher:  %s" % context.teacher.name)

    def test_room_schedule_by_conference(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_schedule',
                    urlconf='gbe.reporting.urls'),
            data={'conf_slug': conf.conference_slug})
        self.assertEqual(response.status_code, 200)
