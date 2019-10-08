from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import ConferenceDayFactory
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


class TestScheduleEmail(TestCase):
    subject = "Your Schedule for Tomorrow at GBE"

    def setUp(self):
        self.client = Client()
        Email.objects.all().delete()

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
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)
        self.assertTrue(context.bid.e_title in queued_email[0].html_message)
        self.assertTrue(
            context.teacher.user_object.email in queued_email[0].to)

    def test_send_for_show(self):
        start_time = datetime.combine(
            datetime.now().date() + timedelta(days=1),
            time(0, 0, 0, 0))
        show_context = ShowContext(starttime=start_time)
        context = ActTechInfoContext(
            show=show_context.show,
            sched_event=show_context.sched_event,
            schedule_rehearsal=True)
        num = schedule_email()
        self.assertEqual(2, num)
        queued_email = Email.objects.filter(
            status=2,
            subject=self.subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 2)
        first = queued_email.filter(
            to=show_context.performer.performer_profile.user_object.email)[0]
        self.assertTrue(show_context.show.e_title in first.html_message)
        second = queued_email.filter(
            to=context.performer.performer_profile.user_object.email)[0]
        self.assertTrue(context.show.e_title in second.html_message)
        self.assertTrue(
            context.rehearsal.eventitem.event.e_title in second.html_message)
