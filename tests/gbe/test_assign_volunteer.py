import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.exceptions import PermissionDenied
from datetime import datetime, date, time
from django.core.urlresolvers import reverse
from django.utils.formats import date_format
import pytz
import re
from tests.factories.gbe_factories import (
    ConferenceFactory,
    GenericEventFactory,
    ProfileFactory,
    UserFactory,
    VolunteerFactory,
    VolunteerWindowFactory,
    VolunteerInterestFactory
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    SchedEventFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    VolunteerContext,
    StaffAreaContext
)
from gbe.models import Conference


class TestAssignVolunteer(TestCase):
    '''Tests for review_volunteer view'''
    view_name = 'volunteer_assign'

    def setUp(self):
        Conference.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

    def set_basic_opportunity(self):
        context = StaffAreaContext()

        current_sched = context.add_volunteer_opp()
        current_sched.starttime = datetime(2016, 2, 5, 12, 0, 0, 0)
        current_sched.max_volunteer = 10
        current_sched.save()

        current_window = VolunteerWindowFactory(
            day__conference=context.conference)

        volunteer = VolunteerFactory(
            b_conference=context.conference,
            submitted=True)
        volunteer.available_windows.add(current_window)
        volunteer.save()

        return {
            'context': context,
            'area': context.area,
            'current_sched': current_sched,
            'current_window': current_window,
            'volunteer': volunteer
        }

    def get_basic_volunteer_to_assign(self):
        data = self.set_basic_opportunity()
        interest = VolunteerInterestFactory(
            volunteer=data['volunteer'])
        data['current_sched'].eventitem.volunteer_type = interest.interest
        data['current_sched'].eventitem.save()
        url = reverse(self.view_name,
                      args=[data['volunteer'].pk],
                      urlconf="gbe.urls")

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        return response, data

    def test_assign_volunteers_bad_user(self):
        ''' user does not have Volunteer Coordinator, permission is denied'''
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        nt.assert_equal(403, response.status_code)

    def test_assign_volunteers_no_profile(self):
        ''' user does not have a profile, permission is denied'''
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        nt.assert_equal(403, response.status_code)

    def test_assign_volunteers_old_bid(self):
        ''' bid is froma past conference'''
        context = VolunteerContext()
        context.conference.status = 'completed'
        context.conference.save()
        url = reverse(self.view_name,
                      args=[context.bid.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertRedirects(response, reverse(
            'volunteer_view',
            urlconf='gbe.urls',
            args=[context.bid.pk]))

    def test_assign_volunteer_show_current_events(self):
        '''conference details show up'''
        response, data = self.get_basic_volunteer_to_assign()

        # event names
        nt.assert_equal(
            response.content.count(str(data['area'])),
            1,
            msg="There should be only 1 parent event")
        nt.assert_equal(
            response.content.count(str(data['current_sched'].eventitem)),
            1,
            msg="There should be 1 schedule items for current_sched.eventitem")

        # start and end times
        nt.assert_in(
            date_format(data['current_sched'].start_time,
                        "SHORT_DATETIME_FORMAT"),
            response.content,
            msg="start time for current_sched didn't show up")
        nt.assert_in(
            date_format(data['current_sched'].end_time,
                        "TIME_FORMAT"),
            response.content,
            msg="end time for current_sched didn't show up")

        # check for volunteer windows
        nt.assert_is_not_none(
            re.search(date_format(data['current_sched'].start_time,
                                  "SHORT_DATETIME_FORMAT"), response.content),
            msg="current_window shows with current_sched is not found")

        nt.assert_equal(
            response.content.count(
                '''<td class="bid-table">10</td>'''),
            1,
            msg="current_sched and unavail_sched should have 10 volunteers")

        # all three volunteer <-> event connections are present
        nt.assert_true(
            "Free<br>" in response.content,
            msg="The volunteer should be free for current_sched event")
        nt.assert_equal(
            response.content.count("Interested<br>"),
            1,
            msg="volunteer vs. event interest did not match for event")
        nt.assert_is_not_none(
            re.search(
                '''<td class="bid-table">\s+N\s+</td>''',
                response.content),
            msg="The current event should be not yet full")

    def test_no_rehearsal_in_events(self):
        '''no rehearsal data shows up'''
        # horrible setup process. Need to fix
        data = self.set_basic_opportunity()

        rehearsal = GenericEventFactory(
            e_conference=data['context'].conference,
            type="Rehearsal Slot")

        rehearsal_slot = SchedEventFactory(
            eventitem=rehearsal,
            starttime=datetime(2016, 2, 6, 13, 0, 0, 0),
            max_volunteer=10)
        EventLabelFactory(event=rehearsal_slot,
                          text=data['context'].conference.conference_slug)

        volunteer = VolunteerFactory(
            b_conference=data['context'].conference,
            submitted=True)
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        nt.assert_not_in(
            str(rehearsal),
            response.content,
            msg="Event Title for rehearsal should not show up")

        nt.assert_not_in(
            date_format(rehearsal_slot.starttime, "SHORT_DATETIME_FORMAT"),
            response.content,
            msg="end time for rehearsal shouldn't show up")

    def test_no_past_conference_details(self):
        '''only current conference events, and windows should be shown'''
        # horrible setup process. Need to fix
        data = self.set_basic_opportunity()
        past_context = StaffAreaContext(
            conference=ConferenceFactory(
                status='completed'))

        past_opp = past_context.add_volunteer_opp()
        past_opp.starttime = datetime(2015, 2, 25, 6, 0, 0, 0)
        past_opp.eventitem.max_volunteer = 10
        past_opp.eventitem.save()

        past_window = VolunteerWindowFactory(
            day__conference=past_context.conference)

        url = reverse(self.view_name,
                      args=[data['volunteer'].pk],
                      urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        nt.assert_not_in(
            str(past_opp.eventitem),
            response.content,
            msg="Event Title for past_opportunity should not show up")
        nt.assert_not_in(
            date_format(past_opp.starttime, "SHORT_DATETIME_FORMAT"),
            response.content,
            msg="start time for past_sched shouldn't show up")

    def test_booking_is_good(self):
        # horrible setup process. Need to fix
        data = self.set_basic_opportunity()

        booked_sched = SchedEventFactory(
            eventitem=data['current_sched'].eventitem,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0),
            max_volunteer=1)
        data['context'].book_volunteer(
            booked_sched,
            volunteer=data['volunteer'].profile)
        EventLabelFactory(event=booked_sched,
                          text=data['context'].conference.conference_slug)
        EventLabelFactory(event=booked_sched,
                          text="Volunteer")

        url = reverse(self.view_name,
                      args=[data['volunteer'].pk],
                      urlconf="gbe.urls")

        login_as(self.privileged_user, self)
        response = self.client.get(url)

        nt.assert_in(
            date_format(booked_sched.start_time, "SHORT_DATETIME_FORMAT"),
            response.content,
            msg="start time for booked_sched didn't show up")
        nt.assert_in(
            date_format(booked_sched.end_time, "SHORT_DATETIME_FORMAT"),
            response.content,
            msg="end time for booked_sched didn't show up")

        nt.assert_is_not_none(
            re.search(
                '''<td class="bid-table">\s+Y\s+</td>''',
                response.content),
            msg="The booked event should show as full")

        # using \ to make sure the formatting of the reg ex is correct.
        checked_box = '''<input id="id_events_\d"\s+name="events"\s''' + \
            '''type="checkbox" value="''' + str(booked_sched.pk) + \
            '''"\s+checked="checked"/>'''
        nt.assert_is_not_none(re.search(
            checked_box,
            response.content),
            msg="The booked event should appear as checked in form")

    def test_assign_volunteer_show_unavailable_event(self):
        '''test how event shows when volunteer not available'''
        data = self.set_basic_opportunity()

        unavail_sched = SchedEventFactory(
            eventitem=data['current_sched'].eventitem,
            starttime=datetime(2016, 2, 7, 12, 0, 0, 0),
            max_volunteer=10)
        EventLabelFactory(event=unavail_sched,
                          text=data['context'].conference.conference_slug)
        EventLabelFactory(event=unavail_sched,
                          text="Volunteer")

        unavail_window = VolunteerWindowFactory(
            day__conference=data['context'].conference,
            day__day=date(2016, 2, 7),
            start=time(11),
            end=time(15))

        volunteer = VolunteerFactory(
            b_conference=data['context'].conference,
            submitted=True)
        VolunteerInterestFactory(
            volunteer=data['volunteer'])
        data['volunteer'].unavailable_windows.add(unavail_window)
        data['volunteer'].save()
        url = reverse(self.view_name,
                      args=[data['volunteer'].pk],
                      urlconf="gbe.urls")

        login_as(self.privileged_user, self)
        response = self.client.get(url)

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Assign Volunteer to Opportunities' in response.content)

        # event names
        nt.assert_equal(
            response.content.count(str(data['current_sched'].eventitem)),
            2,
            msg="There should be 2 schedule items for current_sched.eventitem")

        nt.assert_in(
            date_format(unavail_sched.start_time, "SHORT_DATETIME_FORMAT"),
            response.content,
            msg="start time for unavail_sched didn't show up")
        nt.assert_in(
            date_format(unavail_sched.end_time, "TIME_FORMAT"),
            response.content,
            msg="end time for unavail_sched didn't show up")

        nt.assert_is_not_none(
            re.search(date_format(unavail_sched.start_time,
                                  "SHORT_DATETIME_FORMAT"), response.content),
            msg="unavail_window shows with unavail_sched is not found")

        nt.assert_equal(
            response.content.count(
                '''<td class="bid-table">10</td>'''),
            2,
            msg="unavail_sched and current_sched should have 10 volunteers")

        nt.assert_true(
            "Not Free<br>" in response.content,
            msg="The volunteer should be not free for unavail_sched event")
        nt.assert_is_not_none(
            re.search(
                '''<td class="bid-table">\s+N\s+</td>''',
                response.content),
            msg="The unavailable event should be not yet full")

    def test_volunteer_details(self):
        '''volunteer details show up'''
        response, data = self.get_basic_volunteer_to_assign()
        volunteer = data['volunteer']
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Assign Volunteer to Opportunities' in response.content)

        # volunteer details
        nt.assert_true(volunteer.profile.display_name in response.content)
        nt.assert_true(str(volunteer.number_shifts) in response.content)
        nt.assert_true(
            "Security/usher - Somewhat interested" in
            response.content)
        nt.assert_true(volunteer.opt_outs in response.content)
        nt.assert_true(str(volunteer.pre_event) in response.content)
        nt.assert_true(volunteer.background in response.content)

    def test_post(self):
        ''' test that the post style of request works '''
        data = self.set_basic_opportunity()
        volunteer = data['volunteer']

        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")

        login_as(self.privileged_user, self)
        response = self.client.post(
            url,
            data={'volunteer': volunteer.pk})

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Assign Volunteer to Opportunities' in response.content)

        # volunteer details
        nt.assert_true(volunteer.profile.display_name in response.content)
        nt.assert_true(str(volunteer.number_shifts) in response.content)
        nt.assert_true(volunteer.opt_outs in response.content)
        nt.assert_true(str(volunteer.pre_event) in response.content)
        nt.assert_true(volunteer.background in response.content)
