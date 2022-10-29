import pytest
from django.urls import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.functions.gbe_functions import login_as
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    clear_conferences,
)
from datetime import (
    date,
    datetime,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from gbe.models import (
    UserMessage,
)
from gbetext import (
    full_login_msg,
    no_login_msg,
    pending_note,
    volunteer_instructions,
)


class TestVolunteerSignupView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('volunteer_signup',
                           urlconf="gbe.scheduling.urls")
        cls.profile = ProfileFactory(phone="111-222-3333",
                                     user_object__first_name="Firstname",
                                     user_object__last_name="Lastname")
        clear_conferences()
        cls.conference = ConferenceFactory()
        cls.save_the_date = datetime(2016, 2, 6, 12, 0, 0)
        day = ConferenceDayFactory(
            conference=cls.conference,
            day=date(2016, 0o2, 0o6))
        cls.staffcontext = StaffAreaContext(
            conference=cls.conference,
            starttime=cls.save_the_date)

    def setUp(self):
        self.client = Client()
        self.volunteeropp = self.staffcontext.add_volunteer_opp()

    def basic_event_check(self,
                          response,
                          conference,
                          occurrence,
                          image,
                          action="on"):
        self.assertContains(
            response,
            conference.conference_name)
        self.assertContains(response, occurrence.eventitem.child().e_title)
        self.assertContains(
            response,
            occurrence.start_time.strftime("%-I:%M %p"))
        self.assertContains(
            response,
            occurrence.end_time.strftime("%-I:%M %p"))
        self.assertContains(response, image)
        self.assertContains(response, reverse(
            'set_volunteer',
            args=[occurrence.pk, action],
            urlconf="gbe.scheduling.urls"))

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            full_login_msg % (no_login_msg, reverse(
                'login',
                urlconf='gbe.urls') + "?next=" + self.url))

    def test_signup_w_available_slot(self):
        other_conference = ConferenceFactory(
            status='completed')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(
            response,
            other_conference.conference_name)
        self.basic_event_check(
            response,
            self.staffcontext.conference,
            self.volunteeropp,
            "not_yet_volunteered.gif")
        self.assertContains(response, volunteer_instructions)
        self.assertContains(response, "btn btn-default disabled", 2)

    def test_signup_w_need_approval_slot(self):
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.basic_event_check(
            response,
            self.staffcontext.conference,
            self.volunteeropp,
            "needs_approval.gif")
        self.assertContains(response, pending_note)

    def test_signup_w_signed_up_slot(self):
        UserMessage.objects.all().delete()
        msg = UserMessageFactory(
            view='VolunteerSignupView',
            code='VOLUNTEER_INSTRUCTIONS')
        self.staffcontext.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile)
        login_as(self.profile, self)
        response = self.client.get("%s?conference=%s" % (
            self.url,
            self.staffcontext.conference.conference_slug))
        self.basic_event_check(
            response,
            self.staffcontext.conference,
            self.volunteeropp,
            "volunteered.gif",
            action="off")
        self.assertContains(response, msg.description)

    def test_signup_w_approved_slot(self):
        UserMessage.objects.all().delete()
        msg = UserMessageFactory(
            view='VolunteerSignupView',
            code='PENDING_INSTRUCTIONS')
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        self.staffcontext.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile)
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.basic_event_check(
            response,
            self.staffcontext.conference,
            self.volunteeropp,
            "approved.gif",
            action="off")
        self.assertContains(response, msg.description)

    def test_signup_w_pending_slot(self):
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        self.staffcontext.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile,
            role="Pending Volunteer")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.basic_event_check(
            response,
            self.staffcontext.conference,
            self.volunteeropp,
            "awaiting_approval.gif",
            action="off")
        self.assertContains(response, self.staffcontext.area.description)

    def test_signup_w_waitlisted_volunteer(self):
        self.volunteeropp.approval_needed = True
        self.volunteeropp.save()
        self.staffcontext.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile,
            role="Waitlisted")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.basic_event_check(
            response,
            self.staffcontext.conference,
            self.volunteeropp,
            "awaiting_approval.gif",
            action="off")
        self.assertContains(response, self.staffcontext.area.description)

    def test_other_days(self):
        earlier_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 0o2, 0o5))
        later_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 0o2, 0o7))
        login_as(self.profile, self)
        response = self.client.get("%s?day=02-06-2016" % self.url)
        self.assertContains(response, "?day=02-05-2016")
        self.assertContains(response, "?day=02-07-2016")

    def test_no_conference_days(self):
        clear_conferences()
        ConferenceFactory(status='upcoming')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'This calendar is not currently available.')

    def test_bad_day(self):
        # There is a day, but that's not the day we're asking for.
        url = "%s?day=02-02-2016" % self.url
        login_as(self.profile, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_no_events(self):
        earlier_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 0o2, 0o5))
        login_as(self.profile, self)
        response = self.client.get("%s?day=02-05-2016" % self.url)
        self.assertContains(
            response,
            "There are no volunteer events scheduled for this day.")

    def test_two_upcoming_conf(self):
        second_conference = ConferenceFactory()
        save_the_date = datetime(2017, 2, 6, 12, 0, 0)
        second_day = ConferenceDayFactory(
            conference=second_conference,
            day=date(2017, 0o2, 0o6))
        staffcontext = StaffAreaContext(
            conference=second_conference,
            starttime=save_the_date)
        volunteeropp = staffcontext.add_volunteer_opp()
        login_as(self.profile, self)
        response = self.client.get("%s?conference=%s" % (
            self.url,
            second_conference.conference_slug))
        self.assertContains(
            response,
            staffcontext.conference.conference_name)
        self.assertContains(response, volunteeropp.eventitem.e_title)

    def test_no_space_in_event(self):
        full_opp = self.staffcontext.add_volunteer_opp()
        full_opp.max_volunteer = 0
        full_opp.save()
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, full_opp.eventitem.e_title)

    def test_user_is_rejected(self):
        self.staffcontext.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile,
            role="Rejected")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)

    def test_slot_with_show(self):
        ''' tests both show and an incomplete profile '''
        vol_context = VolunteerContext()
        login_as(vol_context.profile, self)
        response = self.client.get("%s?conference=%s" % (
            self.url,
            vol_context.conference.conference_slug))
        self.basic_event_check(
            response,
            vol_context.conference,
            vol_context.opp_event,
            "volunteered.gif",
            action="off")
        self.assertContains(response, vol_context.event.e_title)
        self.assertContains(response, reverse(
            "detail_view",
            urlconf="gbe.scheduling.urls",
            args=[vol_context.event.pk]))
        self.assertContains(response, "Phone")

    def test_partial_profile(self):
        ''' profile is incomplete, but does have first/last name '''
        profile = ProfileFactory(user_object__first_name="Jane",
                                 user_object__last_name="Jane")
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, "Phone")
        self.assertContains(response, "Jane")
        self.assertContains(response, "Jane")
