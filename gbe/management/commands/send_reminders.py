from django.core.management.base import BaseCommand, CommandError
from gbe_logging import logger
from gbe.email.views import (
    act_tech_reminder,
    sign_form_reminder,
)
from gbe.models import EmailFrequency
from datetime import datetime
from gbetext import day_of_week


class Command(BaseCommand):
    help = '''Sends an email to all upcoming act performers who haven't \
    completed their tech info and/or booked a rehearsal (or ack'd not \
    needing it)'''

    def handle(self, *args, **options):
        sent_anything = False
        sched_days = EmailFrequency.objects.filter(
            email_type="act_tech_reminder").values_list('weekday', flat=True)
        if datetime.now().weekday() in sched_days:
            logger.info('Executing TechReminder ....')
            self.stdout.write('Executing TechReminder....')
            number_emails = act_tech_reminder()
            logger.info('%s tech reminders sent.' % number_emails)
            self.stdout.write('%s tech reminders sent.' % number_emails)
            sent_anything = True

        sched_days = EmailFrequency.objects.filter(
            email_type="sign_form_reminder").values_list('weekday', flat=True)
        if datetime.now().weekday() in sched_days:
            logger.info('Executing SignFormReminder ....')
            self.stdout.write('Executing SignFormReminder....')
            number_emails = sign_form_reminder()
            logger.info('%s sign form reminders sent.' % number_emails)
            self.stdout.write('%s sign form reminders sent.' % number_emails)
            sent_anything = True

        if not sent_anything:
            self.stdout.write(
                'Today is %s, and not a scheduled day for any reminder.' % (
                    day_of_week[datetime.now().weekday()][1]))
