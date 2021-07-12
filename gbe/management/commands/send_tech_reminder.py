from django.core.management.base import BaseCommand, CommandError
from gbe_logging import logger
from gbe.email.views import act_tech_reminder


class Command(BaseCommand):
    help = '''Sends an email to all upcoming act performers who haven't \
    completed their tech info and/or booked a rehearsal (or ack'd not \
    needing it)'''

    def handle(self, *args, **options):
        logger.info('Executing ReminderSend Script....')
        self.stdout.write('Executing ReminderSend Script....')
        number_emails = act_tech_reminder()
        logger.info('%s tech reminders sent.' % number_emails)
        self.stdout.write('%s tech reminders sent.' % number_emails)
