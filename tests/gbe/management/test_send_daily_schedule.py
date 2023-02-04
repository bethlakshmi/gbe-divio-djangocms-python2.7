from django.test import TestCase
from django.test import Client
from gbe.models import Conference
from post_office.models import Email
from django.core.management import call_command
from django.conf import settings
from tests.contexts import ClassContext
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)


class TestSendDailySchedule(TestCase):
    subject = "Your Schedule for Tomorrow at GBE"

    def setUp(self):
        self.client = Client()
        Email.objects.all().delete()
        Conference.objects.all().delete()

    def test_call_command(self):
        start_time = datetime.combine(
            datetime.now().date() + timedelta(days=1),
            time(0, 0, 0, 0))
        context = ClassContext(starttime=start_time)
        call_command("send_daily_schedule")
        queued_email = Email.objects.filter(
            status=2,
            subject=self.subject,
            from_email="Team BurlExpo <%s>" % settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)
        self.assertTrue(context.bid.b_title in queued_email[0].html_message)
        self.assertTrue(
            context.teacher.user_object.email in queued_email[0].to)
