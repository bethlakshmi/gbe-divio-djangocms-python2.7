# -*- coding: utf-8 -*-
import os

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

EMAIL_BACKEND = 'post_office.EmailBackend'
ADMINS = [('Betty','betty@burlesque-expo.com')]
USER_CONTACT_RECIPIENT_ADDRESSES = 'betty@burlesque-expo.com' 

try:
    DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]
except:
    DEFAULT_FROM_EMAIL = 'mail@burlesque-expo.com'

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


# TIME_FORMAT is often used for ending times of events, or when you
# do not need to give the date, such as in calendar grids
GBE_TIME_FORMAT = "%-I:%M %p"
GBE_DATE_FORMAT = "%a, %b %-d"
GBE_DATETIME_FORMAT = GBE_DATE_FORMAT+" "+GBE_TIME_FORMAT
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
DJANGOCMS_STYLE_CHOICES = [
    'container', 
    'content', 
    'font_large', 
    'subtitle', 
    'teaser'
]

FIXTURE_DIRS = ('expo/tests/fixtures',)

EVALUATION_WINDOW = 4
TEXT_CKEDITOR_BASE_PATH = os.path.join(STATIC_URL,
                                       'djangocms_text_ckeditor/ckeditor/')
CKEDITOR_SETTINGS = {
    'stylesSet': [
        {'name': 'Vast Shadow',
         'element': 'h2',
         'styles': {'font-family': 'Vast Shadow',
                    'font-size': '20px'}},
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
        {'name': 'Big', 'element': 'big' },
        {'name': 'Small', 'element': 'small' },
        {'name': 'Typewriter', 'element': 'tt' },
        {'name': 'Computer Code','element': 'code' },
        {'name': 'Keyboard Phrase', 'element': 'kbd' },
        {'name': 'Sample Text', 'element': 'samp' },
        {'name': 'Deleted Text', 'element': 'del' },
        {'name': 'Inserted Text', 'element': 'ins' },
        {'name': 'Cited Work', 'element': 'cite' },
        {'name': 'Inline Quotation', 'element': 'q' },
    ],
    'disableNativeSpellChecker': False,
    'language': 'en',
    'toolbar': 'CMS2',
    'toolbar_CMS2': [
        {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
        {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll', '-', 'Scayt']},
        ['cmsplugins', 'cmswidget'],
        ['Maximize', ''],
        ['Source', '-', 'ShowBlocks'],
        '/',
        {'name': 'basicstyles',
         'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'CopyFormatting',
                   'RemoveFormat']},
        {'name': 'paragraph',
         'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                   'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
        {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
        {'name': 'insert', 'items': ['Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak']},
        '/',
        {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
        {'name': 'colors', 'items': ['TextColor', 'BGColor']},
    ],
    'skin': 'moonocolor',
    'toolbarCanCollapse': False,
}

try:
    MC_API_KEY = os.environ["MC_API_KEY"]
    MC_API_URL = os.environ["MC_API_URL"]
    MC_API_USER = os.environ["MC_API_USER"]
    MC_API_ID = os.environ["MC_API_ID"]
except:
    pass
