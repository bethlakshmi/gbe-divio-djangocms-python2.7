from io import StringIO
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from gbe.models import (
    Conference,
    EmailFrequency,
)
from post_office.models import Email
from django.core.management import call_command
from django.conf import settings
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    EmailFrequencyFactory,
    ProfilePreferencesFactory,
    TechInfoFactory,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from gbetext import day_of_week


class TestSendTechReminder(TestCase):
    subject = "Your Schedule for Tomorrow at GBE"

    def setUp(self):
        self.client = Client()
        Email.objects.all().delete()
        Conference.objects.all().delete()
        EmailFrequency.objects.all().delete()
        EmailFrequencyFactory()

    def test_send_reminder(self):
        incomplete_act_context = ActTechInfoContext()
        incomplete_act_context.act.accepted = 3
        incomplete_act_context.act.save()
        act = incomplete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact)
        call_command("send_tech_reminder")
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Finish your Act Tech Info",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)
        self.assertTrue(act.b_title in queued_email[0].html_message)
        self.assertTrue(
            act.performer.contact.contact_email in queued_email[0].to)
        self.assertTrue(reverse(
            'act_tech_wizard',
            args=[act.pk],
            urlconf='gbe.urls') in queued_email[0].html_message)

    def test_dont_mail_complete_acts(self):
        complete_act_context = ActTechInfoContext(
            schedule_rehearsal=True)
        complete_act_context.act.tech = TechInfoFactory(
            track_artist="",
            track=SimpleUploadedFile("file.mp3", b"file_content"),
            prop_setup="text",
            starting_position="Onstage",
            primary_color="text",
            feel_of_act="text",
            pronouns="text",
            introduction_text="text")
        complete_act_context.act.accepted = 3
        complete_act_context.act.save()
        act = complete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact)
        call_command("send_tech_reminder")
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Finish your Act Tech Info",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)

    def test_dont_mail_complete_acts_no_rehearsal(self):
        complete_act_context = ActTechInfoContext()
        complete_act_context.act.tech = TechInfoFactory(
            confirm_no_rehearsal=True,
            track_artist="",
            track=SimpleUploadedFile("file.mp3", b"file_content"),
            prop_setup="text",
            starting_position="Onstage",
            primary_color="text",
            feel_of_act="text",
            pronouns="text",
            introduction_text="text")
        complete_act_context.act.accepted = 3
        complete_act_context.act.save()
        act = complete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact)
        call_command("send_tech_reminder")
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Finish your Act Tech Info",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)

    def test_obey_email_preference(self):
        incomplete_act_context = ActTechInfoContext()
        incomplete_act_context.act.accepted = 3
        incomplete_act_context.act.save()
        act = incomplete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact,
                                  send_schedule_change_notifications=False)
        call_command("send_tech_reminder")
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Finish your Act Tech Info",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)

    def test_dont_send_today(self):
        EmailFrequency.objects.all().delete()
        incomplete_act_context = ActTechInfoContext()
        incomplete_act_context.act.accepted = 3
        incomplete_act_context.act.save()
        act = incomplete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact)
        out = StringIO()
        call_command("send_tech_reminder", stdout=out)
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Finish your Act Tech Info",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)
        response = out.getvalue()
        self.assertIn('Today is day %s, and not a scheduled day.' % (
            day_of_week[datetime.now().weekday()][1]), response)
