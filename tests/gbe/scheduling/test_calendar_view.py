import pytest
from django.urls import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import clear_conferences
from tests.functions.scheduler_functions import noon
from datetime import (
    date,
    datetime,
    timedelta,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
)
from gbe.models import ConferenceDay
from gbetext import login_please


class TestCalendarView(TestCase):

    @classmethod
    def setUpTestData(cls):
        clear_conferences()
        conference = ConferenceFactory()
        save_the_date = datetime(2016, 2, 6, 12, 0, 0)
        day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 2, 6))
        cls.staffcontext = StaffAreaContext(
            conference=conference,
            starttime=save_the_date)
        cls.showcontext = ShowContext(conference=conference,
                                      starttime=save_the_date)
        cls.other_conference = ConferenceFactory(
            status='completed')
        cls.other_conf_day = ConferenceDayFactory(
            conference=cls.other_conference,
            day=date(2015, 2, 6))
        cls.other_show = ShowContext(conference=cls.other_conference)
        cls.classcontext = ClassContext(
            conference=conference,
            starttime=save_the_date)
        cls.volunteeropp = cls.staffcontext.add_volunteer_opp()

    def setUp(self):
        self.client = Client()

    def test_calendar_generic_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % (
                self.showcontext.conference.conference_name))
        self.assertContains(response, self.showcontext.sched_event.title)
        self.assertContains(
            response,
            self.showcontext.sched_event.starttime.strftime("%-I:%M %p"))
        self.assertContains(
            response,
            self.showcontext.sched_event.end_time.strftime("%-I:%M %p"))
        self.assertNotContains(response, self.other_show.sched_event.title)
        self.assertNotContains(response, self.classcontext.bid.b_title)
        self.assertNotContains(response, self.volunteeropp.title)
        self.assertNotContains(response, reverse(
            'show_dashboard',
            urlconf='gbe.scheduling.urls',
            args=[self.showcontext.sched_event.pk]))

    def test_calendar_priv_dash_link(self):
        profile = ProfileFactory()
        grant_privilege(profile, 'Schedule Mavens')
        login_as(profile, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        response = self.client.get(url)
        self.assertContains(response, self.showcontext.sched_event.title)
        self.assertContains(response, reverse(
            'show_dashboard',
            urlconf='gbe.scheduling.urls',
            args=[self.showcontext.sched_event.pk]))

    def test_calendar_conference_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % (
                self.showcontext.conference.conference_name))
        self.assertNotContains(response, self.showcontext.sched_event.title)
        self.assertNotContains(response, self.other_show.sched_event.title)
        self.assertContains(response, self.classcontext.bid.b_title)
        self.assertContains(response, "Teacher:  %s" % (
            self.classcontext.bid.teacher.name))
        self.assertNotContains(response, self.volunteeropp.title)

    def test_calendar_volunteer_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % (
                self.showcontext.conference.conference_name))
        self.assertNotContains(response, self.showcontext.sched_event.title)
        self.assertNotContains(response, self.other_show.sched_event.title)
        self.assertNotContains(response, self.classcontext.bid.b_title)
        self.assertContains(response, self.volunteeropp.title)

    def test_calendar_conference_w_default_conf_public_days(self):
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 2, 5),
            open_to_public=False)
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 2, 7),
            open_to_public=False)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        response = self.client.get(url)
        self.assertContains(response, "btn disabled", 2)
        self.assertContains(response, "Feb. 6, 2016", 1)

    def test_calendar_volunteer_w_default_conf_public_days(self):
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 2, 5),
            open_to_public=False)
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 2, 7),
            open_to_public=False)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        self.assertNotContains(response, "btn disabled")

    def test_calendar_shows_requested_conference(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'conference': self.other_conference.conference_slug}
        response = self.client.get(url, data=data)
        self.assertNotContains(response, self.showcontext.sched_event.title)
        self.assertContains(response, self.other_show.sched_event.title)

    def test_no_conference_days(self):
        clear_conferences()
        ConferenceFactory(status='upcoming')
        url = reverse('calendar',
                      urlconf='gbe.scheduling.urls',
                      args=['Conference'])
        response = self.client.get(url)
        self.assertContains(
            response,
            'This calendar is not currently available.')

    def test_bad_day(self):
        '''
        There is a day, but that's not the day we're asking for.
        '''
        clear_conferences()
        conference = ConferenceFactory(status='upcoming')
        conference_day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 2, 6))
        url = reverse('calendar',
                      urlconf='gbe.scheduling.urls',
                      args=['Conference'])
        data = {'day': "02-02-2016"}
        response = self.client.get(url, data=data, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_invalid_day(self):
        '''
        There is a day, but that's not the day we're asking for.
        '''
        url = reverse('calendar',
                      urlconf='gbe.scheduling.urls',
                      args=['Conference'])
        data = {'day': "DEADBEEF"}
        response = self.client.get(url, data=data, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_bad_cal_type(self):
        url = reverse('calendar',
                      urlconf='gbe.scheduling.urls',
                      args=['Bad'])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_one_day(self):
        '''
        There is no day but today, so no navigation
        '''
        clear_conferences()
        conference = ConferenceFactory(status='upcoming')
        conference_day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 2, 6))
        url = reverse('calendar',
                      urlconf='gbe.scheduling.urls',
                      args=['Conference'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        self.assertContains(response, "btn disabled", 2)

    def test_day_before(self):
        '''
        There is no day but today, so no navigation
        '''
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        ConferenceDayFactory(
            conference=self.other_conference,
            day=date(2015, 2, 7))
        data = {'day': "02-06-2015"}
        response = self.client.get(url, data=data)
        self.assertContains(
            response,
            '<a href="?day=02-07-2015" ' +
            'data-toggle="tooltip" title="02-07-2015">')

    def test_day_after(self):
        '''
        There is no day but today, so no navigation
        '''
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        ConferenceDayFactory(
            conference=self.other_conference,
            day=date(2015, 2, 7))
        data = {'day': "02-07-2015"}
        response = self.client.get(url, data=data)
        self.assertContains(
            response,
            '<a href="?day=02-06-2015" ' +
            'data-toggle="tooltip" title="02-06-2015">')

    def test_no_sched_events(self):
        '''
        There is a day, but that's not the day we're asking for.
        '''
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        ConferenceDayFactory(
            conference=self.other_conference,
            day=date(2015, 2, 7))
        data = {'day': "02-07-2015"}
        response = self.client.get(url, data=data)
        self.assertContains(
            response,
            "There are no general events scheduled for this day.")

    def test_calendar_1_event_per_hour_w_parent(self):
        self.volunteeropp.parent = self.showcontext.sched_event
        self.volunteeropp.save()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12 col-md-12 col-sm-12 col-12">',
            1)
        self.assertContains(response, self.showcontext.sched_event.slug)
        self.assertNotContains(response, self.showcontext.sched_event.title)

    def test_calendar_2_event_per_hour(self):
        other_show = ShowContext(conference=self.other_conference)
        other_show.sched_event.slug = None
        other_show.sched_event.save()
        two_opp = self.staffcontext.add_volunteer_opp()
        two_opp.parent = other_show.sched_event
        two_opp.save()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-6 col-md-6 col-sm-6 col-12">',
            2)
        self.assertContains(response, two_opp.title)
        self.assertContains(response, other_show.sched_event.title)

    def test_calendar_3_event_per_hour(self):
        self.staffcontext.add_volunteer_opp()
        three_opp = self.staffcontext.add_volunteer_opp()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-4 col-md-4 col-sm-6 col-12">',
            3)

    def test_calendar_4_event_per_hour(self):
        for n in range(0, 2):
            self.staffcontext.add_volunteer_opp()
        three_opp = self.staffcontext.add_volunteer_opp()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-3 col-md-4 col-sm-6 col-12">',
            4)

    def test_calendar_6_event_per_hour(self):
        for n in range(0, 4):
            self.staffcontext.add_volunteer_opp()
        three_opp = self.staffcontext.add_volunteer_opp()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-2 col-md-4 col-sm-6 col-12">',
            6)

    def test_calendar_10_event_per_hour(self):
        for n in range(0, 8):
            self.staffcontext.add_volunteer_opp()
        three_opp = self.staffcontext.add_volunteer_opp()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-2 col-md-4 col-sm-6 col-12">',
            10)

    def test_logged_in_no_interest(self):
        profile = ProfileFactory()
        login_as(profile, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        set_fav_link = reverse(
            "set_favorite",
            args=[self.showcontext.sched_event.pk, "on"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            url))

    def test_logged_in_have_interest(self):
        profile = self.showcontext.set_interest()
        login_as(profile, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        set_fav_link = reverse(
            "set_favorite",
            args=[self.showcontext.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            url))
        self.assertContains(
            response,
            '<div class="col-lg-12 col-md-12 col-sm-12 col-12 interested">')

    def test_logged_in_no_profile(self):
        user = UserFactory()
        login_as(user, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        set_fav_link = reverse(
            "set_favorite",
            args=[self.showcontext.sched_event.pk, "on"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            url))

    def test_calendar_old_conference(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'conference': self.other_conference.conference_slug}
        response = self.client.get(url, data=data)
        self.assertNotContains(response, self.showcontext.sched_event.title)
        set_fav_link = reverse(
            "set_favorite",
            args=[self.showcontext.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.assertNotContains(response, "%s?next=%s" % (
            set_fav_link,
            url))
        set_unfav_link = reverse(
            "set_favorite",
            args=[self.showcontext.sched_event.pk, "on"],
            urlconf="gbe.scheduling.urls")
        self.assertNotContains(response, "%s?next=%s" % (
            set_unfav_link,
            url))

    def test_logged_in_teacher(self):
        login_as(self.classcontext.teacher.performer_profile, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        self.assertContains(
            response,
            '<a href="#" class="cal-favorite detail_link-disabled')
        self.assertContains(
            response,
            '<div class="col-lg-12 col-md-12 col-sm-12 col-12 teacher">')
        self.assertNotContains(response,
                               'fa-tachometer')

    def test_logged_in_performer(self):
        login_as(self.showcontext.performer.performer_profile, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        self.assertContains(
            response,
            '<a href="#" class="cal-favorite detail_link-disabled')
        self.assertContains(
            response,
            '<div class="col-lg-12 col-md-12 col-sm-12 col-12 performer">')

    def test_logged_in_volunteer(self):
        volunteer, booking = self.staffcontext.book_volunteer()
        opportunity = booking.event
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        vol_link = reverse('set_volunteer',
                           args=[opportunity.pk, 'off'],
                           urlconf='gbe.scheduling.urls')
        ConferenceDayFactory(conference=self.staffcontext.conference,
                             day=opportunity.starttime)
        login_as(volunteer, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url, data={
            'day': opportunity.starttime.strftime('%m-%d-%Y')}, follow=True)
        self.assertContains(response, opportunity.title)
        self.assertContains(response,
                            'class="volunteer-icon" alt="You\'ve signed up"/>')
        self.assertContains(response, vol_link)

    def test_volunteer_event_full(self):
        volunteer, booking = self.staffcontext.book_volunteer()
        opportunity = booking.event
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.max_volunteers = 1
        opportunity.save()
        ConferenceDayFactory(conference=self.staffcontext.conference,
                             day=opportunity.starttime)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url, data={
            'day': opportunity.starttime.strftime('%m-%d-%Y')}, follow=True)
        self.assertContains(response, opportunity.title)
        self.assertContains(
          response,
          'This event has all the volunteers it needs.')

    def test_disabled_eval(self):
        eval_profile = self.classcontext.set_eval_answerer()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        login_as(eval_profile, self)
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        eval_link = reverse(
            "eval_event",
            args=[self.classcontext.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertNotContains(response, "%s?next=%s" % (
            eval_link,
            url))
        self.assertContains(response, "You have already rated this class")

    def test_eval_ready(self):
        self.classcontext.setup_eval()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        eval_link = reverse(
            "eval_event",
            args=[self.classcontext.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            eval_link,
            url))
