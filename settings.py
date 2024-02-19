# -*- coding: utf-8 -*-
import os
import aldryn_addons.settings

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'aldryn-addons',
    'aldryn-django',
    'aldryn-sso',
    'aldryn-django-cms',
    'aldryn-common',
    'djangocms-bootstrap4',
    'djangocms-file',
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

PAYPAL_BUY_BUTTON_IMAGE = "/static/img/paysubmit.png"

aldryn_addons.settings.load(locals())


# all django settings can be altered here

INSTALLED_APPS.extend([
    # add your project specific apps here
    'tempus_dominus',
    "scheduler",
    "ticketing",
    "gbe",
    "post_office",
    'paypal.standard.ipn',
    'import_export',
    'snowpenguin.django.recaptcha2',
    'dal',
    'dal_select2',
    'django_addanother',
    'published',

    # Core
    'fobi',

    # Theme
    'fobi.contrib.themes.bootstrap3',

    "fobi.contrib.apps.djangocms_integration",

    # Form field plugins
    'fobi.contrib.plugins.form_elements.fields.boolean',
    'fobi.contrib.plugins.form_elements.fields.checkbox_select_multiple',
    'fobi.contrib.plugins.form_elements.fields.date',
    'fobi.contrib.plugins.form_elements.fields.date_drop_down',
    'fobi.contrib.plugins.form_elements.fields.datetime',
    'fobi.contrib.plugins.form_elements.fields.decimal',
    'fobi.contrib.plugins.form_elements.fields.email',
    'fobi.contrib.plugins.form_elements.fields.file',
    'fobi.contrib.plugins.form_elements.fields.float',
    'fobi.contrib.plugins.form_elements.fields.hidden',
    'fobi.contrib.plugins.form_elements.fields.input',
    'fobi.contrib.plugins.form_elements.fields.integer',
    'fobi.contrib.plugins.form_elements.fields.ip_address',
    'fobi.contrib.plugins.form_elements.fields.null_boolean',
    'fobi.contrib.plugins.form_elements.fields.password',
    'fobi.contrib.plugins.form_elements.fields.radio',
    'fobi.contrib.plugins.form_elements.fields.regex',
    'fobi.contrib.plugins.form_elements.fields.select',
    'fobi.contrib.plugins.form_elements.fields.select_model_object',
    'fobi.contrib.plugins.form_elements.fields.select_multiple',
    'fobi.contrib.plugins.form_elements.fields.select_multiple_model_objects',
    'fobi.contrib.plugins.form_elements.fields.slug',
    'fobi.contrib.plugins.form_elements.fields.text',
    'fobi.contrib.plugins.form_elements.fields.textarea',
    'fobi.contrib.plugins.form_elements.fields.time',
    'fobi.contrib.plugins.form_elements.fields.url',

    # Form element plugins
    'fobi.contrib.plugins.form_elements.content.content_image',
    'fobi.contrib.plugins.form_elements.content.content_image_url',
    'fobi.contrib.plugins.form_elements.content.content_text',
    'fobi.contrib.plugins.form_elements.content.content_video',

    # Form handlers
    'fobi.contrib.plugins.form_handlers.db_store',
    'fobi.contrib.plugins.form_handlers.http_repost',
    'fobi.contrib.plugins.form_handlers.mail',
    'fobi.contrib.plugins.form_handlers.mail_sender',

    # 'debug_toolbar',
])
FOBI_DEFAULT_THEME = 'bootstrap3'
EMAIL_BACKEND = 'post_office.EmailBackend'
ADMINS = [('Betty',
           'betty@burlesque-expo.com',
           'Scratch',
           'info@burlesque-expo.com')]

# MIDDLEWARE += [
#    'debug_toolbar.middleware.DebugToolbarMiddleware', ]
try:
    DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]
except:
    DEFAULT_FROM_EMAIL = 'mail@burlesque-expo.com'

DEFAULT_FROM_NAME = 'Team BurlExpo'

try:
    if os.environ['STAGE'] == 'local':
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
except:
    pass

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
INTERNAL_IPS = [
    '127.0.0.1',
]
# DEBUG_TOOLBAR_CONFIG = {
#    'SHOW_TOOLBAR_CALLBACK': lambda _request: DEBUG
# }

# TIME_FORMAT is often used for ending times of events, or when you
# do not need to give the date, such as in calendar grids
GBE_TIME_FORMAT = "%-I:%M %p"
GBE_DATE_FORMAT = "%a, %b %-d"
GBE_DATETIME_FORMAT = GBE_DATE_FORMAT+" "+GBE_TIME_FORMAT
GBE_TABLE_FORMAT = "%b %-d, %Y, %-I:%M %p"
GBE_SHORT_DATETIME_FORMAT = "%a, "+GBE_TIME_FORMAT
# GBE_DAY_FORMAT = "%A"

try:
    URL_DATE
except:
    URL_DATE = "%m-%d-%Y"

try:
    DURATION_FORMAT
except:
    DURATION_FORMAT = "%-I:%M"

USER_CONTACT_RECIPIENT_ADDRESSES = ['betty@burlesque-expo.com',
                                    'info@burlesque-expo.com']

RECAPTCHA_PRIVATE_KEY = "6Lf1dx0UAAAAANMxh-BqrW_9IU-0n4OZyWin6sGB"
RECAPTCHA_PUBLIC_KEY = "6Lf1dx0UAAAAAMcHUhPsGFc7LUQWHQOfiUWKx1m1"

PAYPAL_TEST = False

if DEBUG:
    RECAPTCHA_PRIVATE_KEY = '6Le0dx0UAAAAACNZynxCx5mUovu3M1Au3XFeeFKN'
    RECAPTCHA_PUBLIC_KEY = '6Le0dx0UAAAAAFGd_HJzX22FdzhwI-GCh8nCoXoU'
    PAYPAL_TEST = True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'gbe.auth.EmailUsernameAuth',
]
DJANGOCMS_STYLE_CHOICES = [
    'container',
    'content',
    'font_large',
    'subtitle',
    'teaser',
]

FIXTURE_DIRS = ('expo/tests/fixtures',)

EVALUATION_WINDOW = 4
TEXT_CKEDITOR_BASE_PATH = os.path.join(STATIC_URL,
                                       'djangocms_text_ckeditor/ckeditor/')
CKEDITOR_SETTINGS = {
    'stylesSet': [
        {'name': 'Montserrat',
         'element': 'font',
         'styles': {'font-family': 'Montserrat'}},
        {'name': 'Limelight',
         'element': 'font',
         'styles': {'font-family': 'Limelight'}},
        {'name': 'Bebas Neue',
         'element': 'font',
         'styles': {'font-family': 'Bebas Neue'}},
        {'name': 'Font Large',
         'element': 'span',
         'styles': {'color': '#000',
                    'font-size': '15.4px',
                    'line-height': '1.5',
                    'font-family': 'Lucida Grande,Tahoma,Verdana,sans-serif'}},
        {'name': 'Italic Title',
         'element': 'h2',
         'styles': {'font-style': 'italic'}},
        {'name': 'Subtitle',
         'element': 'h3',
         'styles': {'color': '#aaa', 'font-style': 'italic'}},
        {'name': 'Special Container',
         'element': 'h2',
         'styles': {'padding': '5px 10px',
                    'background': '#eee',
                    'border': '1px solid #ccc'}},
        {'name': 'Marker',
         'element': 'span',
         'attributes': {'class': 'marker'}},
        {'name': 'Big', 'element': 'big'},
        {'name': 'Small', 'element': 'small'},
        {'name': 'Typewriter', 'element': 'tt'},
        {'name': 'Computer Code', 'element': 'code'},
        {'name': 'Keyboard Phrase', 'element': 'kbd'},
        {'name': 'Sample Text', 'element': 'samp'},
        {'name': 'Deleted Text', 'element': 'del'},
        {'name': 'Inserted Text', 'element': 'ins'},
        {'name': 'Cited Work', 'element': 'cite'},
        {'name': 'Inline Quotation', 'element': 'q'},
    ]
}

# Put this in settings.py
POST_OFFICE = {
    'BATCH_SIZE': 30,
    'THREADS_PER_PROCESS': 1,
}
LOGOUT_REDIRECT_URL = "/gbe/"
LOGIN_URL = "/accounts/login/"

try:
    MC_API_KEY = os.environ["MC_API_KEY"]
    MC_API_URL = os.environ["MC_API_URL"]
    MC_API_USER = os.environ["MC_API_USER"]
    MC_API_ID = os.environ["MC_API_ID"]
except:
    pass

TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "fobi.context_processors.theme")
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "fobi.context_processors.dynamic_values")

CMS_TEMPLATES = (
    (
        "cms_page/{0}/page_with_sidebar.html".format(FOBI_DEFAULT_THEME),
        "General template with sidebar for {0}".format(FOBI_DEFAULT_THEME),
    ),
    (
        "cms_page/{0}/page_without_sidebar.html".format(FOBI_DEFAULT_THEME),
        "General template without sidebar for {0}".format(FOBI_DEFAULT_THEME),
    ),
)
