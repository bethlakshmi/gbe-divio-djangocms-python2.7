from django.core.management.base import BaseCommand, CommandError
from gbe_logging import logger
from ticketing.brown_paper import process_bpt_order_list


class Command(BaseCommand):
    help = '''Imports any new transactions for known BPT purchases'''

    def handle(self, *args, **options):
        logger.info('Executing SyncBPTTrans Script....')
        self.stdout.write('Executing SyncBPTTrans Script....')
        count = process_bpt_order_list()
        logger.info('%s transactions imported.' % count)
        self.stdout.write('%s transactions imported.' % count)
