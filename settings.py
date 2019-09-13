# -*- coding: utf-8 -*-

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'aldryn-addons',
    'aldryn-django',
    'aldryn-sso',
    'aldryn-django-cms',
    'aldryn-common',
    'djangocms-bootstrap4',
    'djangocms-file',
    'djangocms-googlemap',
    'djangocms-history',
    'djangocms-icon',
    'djangocms-link',
    'djangocms-picture',
    'djangocms-snippet',
    'djangocms-style',
    'djangocms-text-ckeditor',
    'djangocms-video',
    'django-filer',
    # </INSTALLED_ADDONS>
]

import aldryn_addons.settings
aldryn_addons.settings.load(locals())


# all django settings can be altered here

INSTALLED_APPS.extend([
    # add your project specific apps here
    "gbe",
    "post_office",
])

try:
    EMAIL_BACKEND
    DEFAULT_FROM_EMAIL
except:
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL = 'gbetest@burlesque-expo.com'
    EMAIL_BACKEND = 'post_office.EmailBackend'



#  Logging settings.
#  Local path and filename to write logs to
try:
    LOG_FILE
except:
    LOG_FILE = 'logs/main.log'
#  Available levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL
try:
    LOG_LEVEL
except:
    LOG_LEVEL = 'INFO'
#  Format for the log file.  Should begin with a timestamp and the log level.
try:
    LOG_FORMAT
except:
    LOG_FORMAT = '%(asctime)s::%(levelname)s::%(funcName)s - %(message)s'


# TIME_FORMAT is often used for ending times of events, or when you
# do not need to give the date, such as in calendar grids
try:
    TIME_FORMAT
except:
    TIME_FORMAT = "%-I:%M %p"

try:
    DATE_FORMAT
except:
    DATE_FORMAT = "%a, %b %-d"
    URL_DATE = "%m-%d-%Y"
try:
    DATETIME_FORMAT
except:
    # Default DATETIME_FORMAT - see 'man date' for format options
    # DATETIME_FORMAT = "%I:%M %p"
    DATETIME_FORMAT = DATE_FORMAT+" "+TIME_FORMAT

try:
    SHORT_DATETIME_FORMAT
except:
    SHORT_DATETIME_FORMAT = "%a, "+TIME_FORMAT

try:
    DURATION_FORMAT
except:
    DURATION_FORMAT = "%-I:%M"

try:
    DAY_FORMAT
except:
    DAY_FORMAT = "%A"

USER_CONTACT_RECIPIENT_ADDRESSES = 'betty@burlesque-expo.com' 
