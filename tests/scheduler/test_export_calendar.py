from django.utils import timezone
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    SchedEventFactory,
)
from gbe.models import (
    Conference,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import (
    ShowContext,
    ClassContext,
)
import pytz
from datetime import (
    date,
    timedelta,
)


class TestExportCalendar(TestCase):
    view_name = 'export_calendar'

    def setUp(self):
        self.client = Client()
        Conference.objects.all().delete()
        self.conference = ConferenceFactory()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.url = reverse(self.view_name,
                           urlconf="scheduler.urls")
        self.showcontext = ShowContext(conference=self.conference)
        self.classcontext = ClassContext(conference=self.conference)

    def make_three_day_spread(self):
        conference_events = [self.showcontext.sched_event,
                             self.classcontext.sched_event]
        two_day = timedelta(2)

        ConferenceDayFactory(conference=self.conference,
                             day=date(2016, 2, 6))
        ConferenceDayFactory(conference=self.conference,
                             day=date(2016, 2, 7))
        conference_events += [self.showcontext.schedule_instance()]
        conference_events += [self.showcontext.schedule_instance(
            starttime=self.showcontext.sched_event.starttime+two_day)]
        conference_events += [self.classcontext.schedule_instance()]
        conference_events += [self.classcontext.schedule_instance(
            starttime=self.classcontext.sched_event.starttime+two_day)]
        return conference_events

    def test_no_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_schedule(self):
        Conference.objects.all().delete()
        show = ShowFactory()
        SchedEventFactory.create(eventitem=show.eventitem_ptr)
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertTrue(response.content.count('\n') == 1)
        self.assertTrue('Session Title' in response.content)

    def test_schedule(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertTrue(response.content.count('\n') > 1)
        self.assertTrue(len(
            (response.content.split('\r\n')[1].split('","'))) >= 8)
        self.assertIn(self.showcontext.show.e_title, response.content)

    def test_guidebook(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertIn(self.showcontext.show.e_title, response.content)
        self.assertIn(self.classcontext.bid.b_title, response.content)

    def test_ical(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url + '?cal_format=ical')
        self.assertTrue('BEGIN:VCALENDAR' in
                        response.content.split('\r\n')[0])
        vevent_count = 0
        for line in response.content.split('\r\n'):
            if 'BEGIN:VEVENT' in line:
                vevent_count = vevent_count + 1
        self.assertTrue(vevent_count > 0)

    def test_type_class(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url + '?event_types=Class')
        self.assertNotIn(self.showcontext.show.e_title, response.content)
        self.assertIn(self.classcontext.bid.b_title, response.content)

    def test_type_show(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url + '?event_types=Show')
        self.assertIn(self.showcontext.show.e_title, response.content)
        self.assertNotIn(self.classcontext.bid.b_title, response.content)

    def test_day_all(self):
        login_as(ProfileFactory(), self)
        event_set = self.make_three_day_spread()
        response = self.client.get(self.url + '?day=All')
        fri_count, sat_count, sun_count = 0, 0, 0
        for line in response.content.split('\r\n'):
            if 'Feb. 5' in line:
                fri_count = fri_count + 1
            elif 'Feb. 6' in line:
                sat_count = sat_count + 1
            elif 'Feb. 7' in line:
                sun_count = sun_count + 1
        self.assertTrue(fri_count == 2 and sat_count == 2 and sun_count == 2)

    def test_day_sat(self):
        login_as(ProfileFactory(), self)
        event_set = self.make_three_day_spread()
        response = self.client.get(self.url + '?day=Saturday')
        fri_count, sat_count, sun_count = 0, 0, 0
        for line in response.content.split('\r\n'):
            if 'Feb. 5' in line:
                fri_count = fri_count + 1
            elif 'Feb. 6' in line:
                sat_count = sat_count + 1
            elif 'Feb. 7' in line:
                sun_count = sun_count + 1
        self.assertTrue(fri_count == 0 and sat_count == 2 and sun_count == 0)
