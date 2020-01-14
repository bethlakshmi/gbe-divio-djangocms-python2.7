import pytest
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.functions.gbe_functions import login_as
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
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
)
from gbe.models import ConferenceDay


class TestCalendarView(TestCase):

    def setUp(self):
        self.client = Client()
        clear_conferences()
        conference = ConferenceFactory()
        save_the_date = datetime(2016, 02, 06, 12, 00, 00)
        day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 02, 06))
        self.staffcontext = StaffAreaContext(
            conference=conference,
            starttime=save_the_date)
        self.showcontext = ShowContext(conference=conference,
                                       starttime=save_the_date)
        self.other_conference = ConferenceFactory(
            status='completed')
        self.other_conf_day = ConferenceDayFactory(
            conference=self.other_conference,
            day=date(2015, 02, 06))
        self.other_show = ShowContext(conference=self.other_conference)
        self.classcontext = ClassContext(
            conference=conference,
            starttime=save_the_date)
        self.volunteeropp = self.staffcontext.add_volunteer_opp()

    def test_calendar_generic_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % (
                self.showcontext.conference.conference_name))
        self.assertContains(response, self.showcontext.show.e_title)
        self.assertContains(
            response,
            self.showcontext.sched_event.starttime.strftime("%-I:%M %p"))
        self.assertContains(
            response,
            self.showcontext.sched_event.end_time.strftime("%-I:%M %p"))
        self.assertNotContains(response, self.other_show.show.e_title)
        self.assertNotContains(response, self.classcontext.bid.e_title)
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)

    def test_calendar_conference_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % (
                self.showcontext.conference.conference_name))
        self.assertNotContains(response, self.showcontext.show.e_title)
        self.assertNotContains(response, self.other_show.show.e_title)
        self.assertContains(response, self.classcontext.bid.e_title)
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)

    def test_calendar_volunteer_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % (
                self.showcontext.conference.conference_name))
        self.assertNotContains(response, self.showcontext.show.e_title)
        self.assertNotContains(response, self.other_show.show.e_title)
        self.assertNotContains(response, self.classcontext.bid.e_title)
        self.assertContains(response, self.volunteeropp.eventitem.e_title)

    def test_calendar_conference_w_default_conf_public_days(self):
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 02, 05),
            open_to_public=False)
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 02, 07),
            open_to_public=False)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        response = self.client.get(url)
        self.assertContains(response, "btn btn-default disabled", 2)
        self.assertContains(response, "Feb. 6, 2016", 1)

    def test_calendar_volunteer_w_default_conf_public_days(self):
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 02, 05),
            open_to_public=False)
        conference_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 02, 07),
            open_to_public=False)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        self.assertNotContains(response, "btn btn-default disabled")

    def test_calendar_shows_requested_conference(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'conference': self.other_conference.conference_slug}
        response = self.client.get(url, data=data)
        self.assertNotContains(response, self.showcontext.show.e_title)
        self.assertContains(response, self.other_show.show.e_title)

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
            day=date(2016, 02, 06))
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
            day=date(2016, 02, 06))
        url = reverse('calendar',
                      urlconf='gbe.scheduling.urls',
                      args=['Conference'])
        data = {'day': "02-06-2016"}
        response = self.client.get(url, data=data)
        self.assertContains(response, "btn btn-default disabled", 2)

    def test_day_before(self):
        '''
        There is no day but today, so no navigation
        '''
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        ConferenceDayFactory(
            conference=self.other_conference,
            day=date(2015, 02, 07))
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
            day=date(2015, 02, 07))
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
            day=date(2015, 02, 07))
        data = {'day': "02-07-2015"}
        response = self.client.get(url, data=data)
        self.assertContains(
            response,
            "There are no general events scheduled for this day.")

    def test_calendar_1_event_per_hour(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12 col-md-12 col-sm-12 col-12 ">',
            1)

    def test_calendar_2_event_per_hour(self):
        two_opp = self.staffcontext.add_volunteer_opp()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-6 col-md-6 col-sm-6 col-12 ">',
            2)
        self.assertContains(response, two_opp.eventitem.e_title)

    def test_calendar_3_event_per_hour(self):
        self.staffcontext.add_volunteer_opp()
        three_opp = self.staffcontext.add_volunteer_opp()
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-4 col-md-4 col-sm-6 col-12 ">',
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
            '<div class="col-lg-3 col-md-4 col-sm-6 col-12 ">',
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
            '<div class="col-lg-2 col-md-4 col-sm-6 col-12 ">',
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
            '<div class="col-lg-2 col-md-4 col-sm-6 col-12 ">',
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
        self.assertNotContains(response, self.showcontext.show.e_title)
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

        self.assertContains(response,
                            '<a href="#" class="detail_link-disabled')
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
        self.assertContains(response,
                            '<a href="#" class="detail_link-disabled')
        self.assertContains(
            response,
            '<div class="col-lg-12 col-md-12 col-sm-12 col-12 performer">')

    def test_logged_in_volunteer(self):
        volunteer, booking = self.staffcontext.book_volunteer()
        login_as(volunteer, self)
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-6 col-md-6 col-sm-6 col-12 volunteer">')
        self.assertContains(response,
                            '<a href="#" class="detail_link-disabled')

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
