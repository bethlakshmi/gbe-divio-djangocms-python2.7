from django.core.management.base import BaseCommand, CommandError
from gbe_logging import logger
from ticketing.eventbrite import (
    import_eb_ticket_items,
    process_eb_purchases,
)


class Command(BaseCommand):
    help = '''Imports any new transactions, tickets and events for EB org'''

    def handle(self, *args, **options):
        logger.info('Executing Sync EB Script....')
        self.stdout.write('Executing Sync EB Script....')
        msg, is_success = import_eb_ticket_items()
        logger.info(msg)
        self.stdout.write(msg)
        msg, is_success = process_eb_purchases()
        logger.info(msg)
        self.stdout.write(msg)
