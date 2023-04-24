from django.urls import reverse
from datetime import (
    date,
    timedelta,
)
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


class TestReports(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()

    def test_list_reports_by_conference(self):
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('report_list',
                    urlconf="gbe.reporting.urls"),
            data={"conf_slug": conf.conference_slug})
        self.assertEqual(response.status_code, 200)

    def test_list_reports_fail(self):
        '''list_reports view should fail because user
           is not in one of the privileged groups
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse('report_list',
                    urlconf="gbe.reporting.urls"))
        self.assertEqual(response.status_code, 403)

    def test_list_reports_succeed(self):
        '''list_reports view should load, user has proper
           privileges
        '''
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('report_list',
                    urlconf="gbe.reporting.urls"))
        self.assertEqual(response.status_code, 200)

    def test_room_schedule_fail(self):
        '''room_schedule view should load for privileged users,
           and fail for others
        '''
        current_conference = ConferenceFactory()
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_schedule',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 403)

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
                    urlconf='gbe.reporting.urls',
                    args=[context.room.pk]))
        self.assertEqual(response.status_code, 200)

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

    def test_room_setup_not_visible_without_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        current_conference = ConferenceFactory()
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_setup',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 403)

    def test_room_setup_visible_with_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        current_conference = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_setup',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 200)

    def test_room_setup_by_conference_with_permission(self):
        '''room_setup view should load for privileged users,
           and fail for others
        '''
        Conference.objects.all().delete()
        context = ClassContext()
        context.bid.space_needs = 5
        context.bid.save()
        one_day = timedelta(1)
        ConferenceDayFactory(conference=context.conference,
                             day=context.sched_event.starttime.date())
        ConferenceDayFactory(
            conference=context.conference,
            day=context.sched_event.starttime.date()+one_day)
        context.schedule_instance(
            starttime=context.sched_event.starttime + one_day)
        current_conference = context.conference
        ConferenceDayFactory(conference=context.conference,
                             day=context.sched_event.starttime.date())
        current_conference = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('room_setup', urlconf='gbe.reporting.urls'),
            data={'conf_slug': context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, context.bid.b_title, 2)
        self.assertContains(response, space_options[1][1][1][1])
