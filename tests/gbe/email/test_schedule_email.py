from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    ProfilePreferencesFactory,
)
from tests.contexts import (
    ActTechInfoContext,
    ClassContext,
    ShowContext,
)
from post_office.models import Email
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from gbe.email.views import schedule_email
from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse


class TestScheduleEmail(TestCase):
    subject = "Your Schedule for Tomorrow at GBE"
    get_param = "?email_disable=send_daily_schedule"

    def setUp(self):
        self.client = Client()
        Email.objects.all().delete()
        self.unsub_link = Site.objects.get_current().domain + reverse(
            'email_update',
            urlconf='gbe.urls')

    def test_no_conference_day(self):
        num = schedule_email()
        self.assertEqual(0, num)

    def test_conf_day_no_receivers(self):
        ConferenceDayFactory(day=date.today() + timedelta(days=1))
        num = schedule_email()
        self.assertEqual(0, num)

    def test_send_to_teacher(self):
        start_time = datetime.combine(
            datetime.now().date() + timedelta(days=1),
            time(0, 0, 0, 0))
        context = ClassContext(starttime=start_time)
        num = schedule_email()
        self.assertEqual(1, num)
        queued_email = Email.objects.filter(
            status=2,
            subject=self.subject,
            from_email="Team BurlExpo <%s>" % settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)
        self.assertTrue(context.bid.b_title in queued_email[0].html_message)
        self.assertTrue(self.unsub_link in queued_email[0].html_message)
        self.assertTrue(self.get_param in queued_email[0].html_message)
        self.assertTrue(
            context.teacher.user_object.email in queued_email[0].to)

    def test_send_for_show(self):
        start_time = datetime.combine(
            datetime.now().date() + timedelta(days=1),
            time(0, 0, 0, 0))
        show_context = ShowContext(starttime=start_time)
        context = ActTechInfoContext(
            sched_event=show_context.sched_event,
            schedule_rehearsal=True,
            conference=show_context.conference)
        num = schedule_email()
        queued_email = Email.objects.filter(
            status=2,
            subject=self.subject,
            from_email="Team BurlExpo <%s>" % settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(2, num)
        self.assertEqual(queued_email.count(), 2)
        first = queued_email.filter(
            to=show_context.performer.contact.user_object.email)[0]
        self.assertTrue(show_context.sched_event.title in first.html_message)
        self.assertTrue(self.unsub_link in queued_email[0].html_message)
        self.assertTrue(self.get_param in queued_email[0].html_message)
        second = queued_email.filter(
            to=context.performer.contact.user_object.email)[0]
        self.assertTrue(context.sched_event.title in second.html_message)
        self.assertTrue(
            context.rehearsal.title in second.html_message)

    def test_exclude_unsubscribed(self):
        start_time = datetime.combine(
            datetime.now().date() + timedelta(days=1),
            time(0, 0, 0, 0))
        context = ClassContext(starttime=start_time)
        ProfilePreferencesFactory(
            profile=context.teacher.contact,
            send_daily_schedule=False)
        num = schedule_email()
        self.assertEqual(0, num)
        queued_email = Email.objects.filter(
            status=2,
            subject=self.subject,
            from_email="Team BurlExpo <%s>" % settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)
