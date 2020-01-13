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
    UserMessageFactory,
)
from tests.functions.gbe_functions import clear_conferences
from tests.functions.scheduler_functions import noon
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
    pending_note,
    role_options,
    volunteer_instructions,
)


class TestVolunteerSignupView(TestCase):

    def setUp(self):
        self.url = reverse('volunteer_signup',
                           urlconf="gbe.scheduling.urls")
        self.client = Client()
        self.profile = ProfileFactory()
        clear_conferences()
        conference = ConferenceFactory()
        save_the_date = datetime(2016, 02, 06, 12, 00, 00)
        day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 02, 06))
        self.staffcontext = StaffAreaContext(
            conference=conference,
            starttime=save_the_date)
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

    def test_signup_w_available_slot(self):
        other_conference = ConferenceFactory(
            status='completed')
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

    def test_other_days(self):
        earlier_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 02, 05))
        later_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 02, 07))
        login_as(self.profile, self)
        response = self.client.get("%s?day=02-06-2016" % self.url)
        self.assertContains(response, "?day=02-05-2016")
        self.assertContains(response, "?day=02-07-2016")

    def test_no_conference_days(self):
        clear_conferences()
        ConferenceFactory(status='upcoming')
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'This calendar is not currently available.')

    def test_bad_day(self):
        #There is a day, but that's not the day we're asking for.
        url = "%s?day=02-02-2016" % self.url
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_no_events(self):
        earlier_day = ConferenceDayFactory(
            conference=self.staffcontext.conference,
            day=date(2016, 02, 05))
        login_as(self.profile, self)
        response = self.client.get("%s?day=02-05-2016" % self.url)
        self.assertContains(response, "There are no volunteer events " +
            "scheduled for this day.")

    def test_two_upcoming_conf(self):
        second_conference = ConferenceFactory()
        save_the_date = datetime(2017, 02, 06, 12, 00, 00)
        second_day = ConferenceDayFactory(
            conference=second_conference,
            day=date(2017, 02, 06))
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

        response = self.client.get(self.url)
        self.assertNotContains(response, full_opp.eventitem.e_title)

    def test_user_is_staff_lead(self):
        self.staffcontext.book_volunteer(
            volunteer_sched_event=self.volunteeropp,
            volunteer=self.profile,
            role="Staff Lead")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)

    def test_slot_with_show(self):
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
