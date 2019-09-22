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
    "tinymce",
    "scheduler",
    "ticketing",
    "gbe",
    "post_office",
    'import_export',
    'snowpenguin.django.recaptcha2',
])

try:
    EMAIL_BACKEND
    DEFAULT_FROM_EMAIL
except:
    EMAIL_HOST = 'secure135.inmotionhosting.com'
    EMAIL_PORT = 465
    EMAIL_HOST_USER = 'mail@burlesque-expo.com'
    EMAIL_HOST_PASSWORD = '_uWeK9,+tR5^'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'mail@burlesque-expo.com'
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
GBE_TIME_FORMAT = "%-I:%M %p"
GBE_DATE_FORMAT = "%a, %b %-d"
GBE_DATETIME_FORMAT = GBE_DATE_FORMAT+" "+GBE_TIME_FORMAT
GBE_SHORT_DATETIME_FORMAT = "%a, "+GBE_TIME_FORMAT
#GBE_DAY_FORMAT = "%A"

try:
    URL_DATE
except:
    URL_DATE = "%m-%d-%Y"

try:
    DURATION_FORMAT
except:
    DURATION_FORMAT = "%-I:%M"

USER_CONTACT_RECIPIENT_ADDRESSES = 'betty@burlesque-expo.com'

RECAPTCHA_PRIVATE_KEY = '6Le0dx0UAAAAACNZynxCx5mUovu3M1Au3XFeeFKN'
RECAPTCHA_PUBLIC_KEY = '6Le0dx0UAAAAAFGd_HJzX22FdzhwI-GCh8nCoXoU'

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,paste,searchreplace, insertdatetime",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'theme_advanced_buttons1': "bold,italic,underline,|,justifyleft," +
    "justifycenter,justifyright,fontselect,fontsizeselect,formatselect," +
    "forecolor,backcolor",
    'theme_advanced_buttons2': "cut,copy,paste,|,bullist,numlist,|," +
    "outdent,indent,|,undo,redo,|,link,unlink,anchor,image,|,code,preview," +
    "|,search, replace",
    'theme_advanced_buttons3': "insertdate,inserttime,|,advhr,,removeformat," +
    "|,sub,sup,|,charmap,emotions, tablecontrols",
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'gbe.auth.EmailUsernameAuth',
]
