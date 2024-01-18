from django.core.management.base import BaseCommand, CommandError
from gbe_logging import logger
from ticketing.humanitix import HumanitixClient


class Command(BaseCommand):
    help = '''Imports any new transactions, tickets and events for HT org'''

    def handle(self, *args, **options):
        logger.info('Executing Sync HT Script....')
        self.stdout.write('Executing Sync HT Script....')
        humanitix = HumanitixClient()
        msg, is_success = humanitix.import_ticket_items()
        logger.info(msg)
        self.stdout.write(msg)
        msgs = humanitix.process_transactions()
        for sub_msg, is_success in msgs:
            if not is_success:
                logger.info(sub_msg)
                self.stdout.write(sub_msg)
            else:
                raise Exception(sub_msg)
