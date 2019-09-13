#  Wrapper and skeleton for logging messages to a log file

from logging import *

from settings import LOG_FILE
from settings import LOG_LEVEL
from settings import LOG_FORMAT

logger = getLogger(__name__)
basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format=LOG_FORMAT)


def log_func(funct):
    '''
    Use as a decorator to log a function call or similar on the info level.
    '''

    def __call__(*args, **kwargs):
        if LOG_LEVEL in ('debug', 'error', 'critical'):

            out_text = funct.func_name+' - args :\n'+str(args)+'\n---------\nkwargs:\n'+str(kwargs)+'\n---------\n'
        else:
            out_text = funct.func_name
        logger.info(out_text)
        return funct(*args, **kwargs)
    return __call__


def memusage():
    '''
    Returns the memory footprint of the current instance, in kilobytes.
    '''

    from resource import getrusage, RUSAGE_SELF
    return str(getrusage(RUSAGE_SELF).ru_maxrss)


def log_import(module_names, source):
    logger.info("Import %s from %s, VmSize: %s" % (
        ','.join(module_names),
        source,
        memusage()))
