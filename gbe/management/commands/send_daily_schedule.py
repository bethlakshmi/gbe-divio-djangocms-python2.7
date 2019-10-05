from django.core.management.base import BaseCommand, CommandError
from gbe_logging import logger
from gbe.email.views import schedule_email


class Command(BaseCommand):
    help = '''Sends an email with tomorrow's schedule to anyone with a \
    commitment starting that day'''

    def handle(self, *args, **options):
        logger.info('Executing ScheduleSend Script....')
        self.stdout.write('Executing ScheduleSend Script....')
        number_emails = schedule_email()
        logger.info('%s schedule notifications sent.' % number_emails)
        self.stdout.write('%s schedule notifications sent.' % number_emails)
