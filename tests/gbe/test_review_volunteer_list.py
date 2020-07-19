import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    ProfilePreferencesFactory,
    UserFactory,
    VolunteerFactory,
    VolunteerInterestFactory
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    ResourceAllocationFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from scheduler.models import Event as sEvent
from datetime import datetime, date, time
from django.utils.formats import date_format
import pytz
from scheduler.models import (
    Worker,
    EventContainer
)


class TestReviewVolunteerList(TestCase):
    '''Tests for review_volunteer_list view'''
    view_name = 'volunteer_review_list'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

        self.volunteer = VolunteerFactory(
            submitted=True,
            profile__user_object__email="review_vol@testemail.com")
        self.prefs = ProfilePreferencesFactory(
            profile=self.volunteer.profile,
            in_hotel="Maybe",
            inform_about=True,
            show_hotel_infobox=True)
        self.url = reverse(self.view_name, urlconf='gbe.urls')

    def test_review_volunteer_all_well(self):
        '''default conference selected, make sure it returns the right page'''
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)

        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, 'Bid Information')

    def test_review_volunteer_w_conf(self):
        ''' when a specific conf has specific bids, check bid details'''
        volunteer = VolunteerFactory(
            submitted=True)
        interest = VolunteerInterestFactory(
            volunteer=self.volunteer
        )
        volunteer.profile.user_object.email = "review_vol@testemail.com"
        volunteer.profile.user_object.save()
        prefs = ProfilePreferencesFactory(
            profile=volunteer.profile,
            in_hotel="Maybe",
            inform_about=True,
            show_hotel_infobox=True)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            {'conf_slug': self.volunteer.b_conference.conference_slug})

        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, 'Bid Information')
        self.assertContains(response, str(self.volunteer.number_shifts))
        self.assertContains(response, self.volunteer.background)
        self.assertContains(response, self.volunteer.profile.display_name)
        self.assertContains(response, interest.interest.interest)
        self.assertContains(response, self.volunteer.profile.user_object.email)
        self.assertContains(response, self.prefs.in_hotel)
        self.assertContains(response, "Needs Review")
        self.assertContains(response, "Review")

    def test_review_volunteer_as_coordinator(self):
        ''' volunteer coordinators get special privileges'''
        coord_profile = ProfileFactory()
        grant_privilege(coord_profile, 'Volunteer Reviewers')
        grant_privilege(coord_profile, 'Volunteer Coordinator')

        login_as(coord_profile, self)
        response = self.client.get(
            self.url,
            {'conf_slug': self.volunteer.b_conference.conference_slug})

        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, 'Bid Information')
        self.assertContains(response, str(self.volunteer.number_shifts))
        self.assertContains(response, self.volunteer.background)
        self.assertContains(response, self.volunteer.profile.display_name)
        self.assertContains(response, self.volunteer.profile.user_object.email)
        self.assertContains(response, self.prefs.in_hotel)
        self.assertContains(response, "Needs Review")
        self.assertContains(response, "Review")

    def test_review_volunteer_has_commitments(self):
        ''' when a volunteer is already booked somewhere, it should show up'''

        current_opportunity = GenericEventFactory(
            e_conference=self.volunteer.b_conference,
            volunteer_type=AvailableInterestFactory(interest='Security/usher'),
            type='Volunteer')
        current_opportunity.save()
        booked_sched = sEvent(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0),
            max_volunteer=1)
        booked_sched.save()
        worker = Worker(_item=self.volunteer.profile, role='Volunteer')
        worker.save()
        volunteer_assignment = ResourceAllocationFactory(
            event=booked_sched,
            resource=worker
        )
        EventLabelFactory(event=booked_sched,
                          text=self.volunteer.b_conference.conference_slug)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            {'conf_slug': self.volunteer.b_conference.conference_slug})

        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, 'Bid Information')
        self.assertContains(
            response,
            str(current_opportunity),
            1,
            msg_prefix="The commitment %s is not showing up" % (
                str(current_opportunity)))
        self.assertContains(
            response,
            date_format(booked_sched.start_time, "DATETIME_FORMAT"),
            msg_prefix="start time for commitment (%s) didn't show up" % (
                date_format(booked_sched.start_time, "DATETIME_FORMAT")))
        self.assertContains(
            response,
            date_format(booked_sched.end_time, "TIME_FORMAT"),
            msg_prefix="end time for commitment (%s) didn't show up" % (
                date_format(booked_sched.end_time, "TIME_FORMAT")))

    def test_review_volunteer_has_old_commitments(self):
        ''' when a volunteer is booked in old conference, it should not show'''
        past_conference = ConferenceFactory(accepting_bids=False,
                                            status='completed')
        past_opportunity = GenericEventFactory(
            e_conference=past_conference,
            volunteer_type=AvailableInterestFactory(interest='Security/usher'),
            type='Volunteer')
        past_opportunity.save()
        booked_sched = sEvent(
            eventitem=past_opportunity,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0),
            max_volunteer=1)
        booked_sched.save()
        worker = Worker(_item=self.volunteer.profile, role='Volunteer')
        worker.save()
        volunteer_assignment = ResourceAllocationFactory(
            event=booked_sched,
            resource=worker
        )
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            {'conf_slug': self.volunteer.b_conference.conference_slug})

        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, 'Bid Information')
        self.assertNotContains(
            response,
            str(past_opportunity),
            msg_prefix="The commitment %s is showing up" % (
                str(past_opportunity)))

    def test_review_volunteer_bad_user(self):
        ''' user does not have the right privilege and permission is denied'''
        login_as(ProfileFactory(), self)
        response = self.client.get(
            self.url,
            {'conf_slug': self.volunteer.b_conference.conference_slug})
        nt.assert_equal(response.status_code, 403)

    def test_review_volunteer_no_profile(self):
        ''' user does not have a profile, gets permission denied'''
        login_as(UserFactory(), self)
        response = self.client.get(
            self.url,
            {'conf_slug': self.volunteer.b_conference.conference_slug})
        nt.assert_equal(response.status_code, 403)

    def test_review_volunteer_inactive_user(self):
        '''default conference selected, make sure it returns the right page'''
        inactive = VolunteerFactory(
            submitted=True,
            profile__user_object__email="review_vol@testemail.com",
            profile__user_object__is_active=False)
        interest = VolunteerInterestFactory(
            volunteer=inactive
        )
        ProfilePreferencesFactory(
            profile=inactive.profile,
            in_hotel="Maybe",
            inform_about=True,
            show_hotel_infobox=True)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            {'conf_slug': inactive.b_conference.conference_slug})
        self.assertContains(response, 'bid-table danger')
