from io import StringIO
from django.test import TestCase
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
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    RoleExclusionFactory,
)
from tests.functions.ticketing_functions import set_form


class TestSendReminder(TestCase):
    subject = "Your Schedule for Tomorrow at GBE"

    @classmethod
    def setUpTestData(cls):
        EmailFrequency.objects.all().delete()
        EmailFrequencyFactory()
        EmailFrequencyFactory(email_type="sign_form_reminder")

    def setUp(self):
        Email.objects.all().delete()
        Conference.objects.all().delete()

    def test_send_act_tech_reminder(self):
        incomplete_act_context = ActTechInfoContext()
        incomplete_act_context.act.accepted = 3
        incomplete_act_context.act.save()
        act = incomplete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact)
        call_command("send_reminders")
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Finish your Act Tech Info",
            from_email="Team BurlExpo <%s>" % settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)
        self.assertTrue(act.b_title in queued_email[0].html_message)
        self.assertTrue(
            act.performer.contact.contact_email in queued_email[0].to)
        self.assertTrue(reverse(
            'act_tech_wizard',
            args=[act.pk],
            urlconf='gbe.urls') in queued_email[0].html_message)

    def test_sign_form_reminder(self):
        context = ActTechInfoContext()
        condition = RoleEligibilityConditionFactory(
            role="Performer",
            checklistitem__description="Form to Sign!",
            checklistitem__e_sign_this=set_form())
        RoleExclusionFactory(condition=condition)
        ProfilePreferencesFactory(profile=context.performer.contact)
        call_command("send_reminders")
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Sign Forms",
            from_email="Team BurlExpo <%s>" % settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 1)
        self.assertTrue(
            context.performer.contact.contact_email in queued_email[0].to)
        self.assertTrue(reverse(
            'sign_forms',
            urlconf='ticketing.urls') in queued_email[0].html_message)

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
            introduction_text="text")
        complete_act_context.act.accepted = 3
        complete_act_context.act.save()
        act = complete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact)
        call_command("send_reminders")
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
            introduction_text="text")
        complete_act_context.act.accepted = 3
        complete_act_context.act.save()
        act = complete_act_context.act
        ProfilePreferencesFactory(profile=act.performer.contact)
        call_command("send_reminders")
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
        call_command("send_reminders")
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
        call_command("send_reminders", stdout=out)
        queued_email = Email.objects.filter(
            status=2,
            subject="Reminder to Finish your Act Tech Info",
            from_email=settings.DEFAULT_FROM_EMAIL,
            )
        self.assertEqual(queued_email.count(), 0)
        response = out.getvalue()
        self.assertIn(
            'Today is %s, and not a scheduled day for any reminder.' % (
                day_of_week[datetime.now().weekday()][1]), response)
        EmailFrequencyFactory()
        EmailFrequencyFactory(email_type="sign_form_reminder")
