import os

"""
Django test settings for expo project.

Because divio injects a lot, this is much bigger than the settings.py as it
also covers what divio configures out of our settings.py view.

"""

os.environ["DEBUG"] = "False"

try:
    from settings import *
except:
    pass

try:
    BASE_DIR
except:
    BASE_DIR = '/app'

try:
    STATIC_URL
except:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')
    STATIC_URL = '/static/'
    LOGIN_REDIRECT_URL = '/'
    LOGIN_URL = '/login/'

INSTALLED_APPS = [
    'aldryn_addons',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'aldryn_sso',
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'aldryn_django',
    'aldryn_sites',
    'cms',
    'aldryn_django_cms',
    'menus',
    'sekizai',
    'tempus_dominus',
    'treebeard',
    'parler',
    'django.contrib.sitemaps',
    'compressor',
    'robots',
    'captcha',
    'django_select2',
    'filer.contrib.django_cms',
    'djangocms_icon',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_bootstrap4',
    'djangocms_bootstrap4.contrib.bootstrap4_alerts',
    'djangocms_bootstrap4.contrib.bootstrap4_badge',
    'djangocms_bootstrap4.contrib.bootstrap4_card',
    'djangocms_bootstrap4.contrib.bootstrap4_carousel',
    'djangocms_bootstrap4.contrib.bootstrap4_collapse',
    'djangocms_bootstrap4.contrib.bootstrap4_content',
    'djangocms_bootstrap4.contrib.bootstrap4_grid',
    'djangocms_bootstrap4.contrib.bootstrap4_jumbotron',
    'djangocms_bootstrap4.contrib.bootstrap4_link',
    'djangocms_bootstrap4.contrib.bootstrap4_listgroup',
    'djangocms_bootstrap4.contrib.bootstrap4_media',
    'djangocms_bootstrap4.contrib.bootstrap4_picture',
    'djangocms_bootstrap4.contrib.bootstrap4_tabs',
    'djangocms_bootstrap4.contrib.bootstrap4_utilities',
    'djangocms_file',
    'djangocms_history',
    'djangocms_snippet',
    'djangocms_style',
    'djangocms_text_ckeditor',
    'djangocms_video',
    'filer',
    'paypal.standard.ipn',
    'easy_thumbnails',
    'polymorphic',
    'scheduler',
    'ticketing',
    'gbe',
    'post_office',
    'import_export',
    'django_recaptcha',
    'dal',
    'dal_select2',
    'django_addanother',
]

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
try:
    SECRET_KEY
except:
    SECRET_KEY = '0sdq74686*ayl^0!tqlt*!mgsycr)h4h#*4*_x=2_dw9cq8d!i'

PAYPAL_BUY_BUTTON_IMAGE = "/static/img/paysubmit.png"
PAYPAL_TEST = True

try:
    TEMPLATES
except:

    TEMPLATES = [{
        'DIRS': [os.path.join(BASE_DIR, "templates"), ],
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.static',
                'aldryn_django.context_processors.debug',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'aldryn_snake.template_api.template_processor'],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader']},
        'BACKEND': 'django.template.backends.django.DjangoTemplates'}]

MIDDLEWARE = (
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'aldryn_django.middleware.LanguagePrefixFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'aldryn_sites.middleware.SiteMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
)

try:
    ROOT_URLCONF
except:
    ROOT_URLCONF = 'urls'
    WSGI_APPLICATION = 'wsgi.application'
    ADDONS_DEV_DIR = os.path.join(BASE_DIR, "addons-dev")
    ADDONS_DIR = os.path.join(BASE_DIR, '/addons')
    ADDON_URLS = ['aldryn_django_cms.urls', 'filer.server.urls']
    ADDON_URLS_I18N = ['aldryn_django.i18n_urls',
                       'aldryn_django_cms.urls_i18n']
    ADDON_URLS_I18N_LAST = 'cms.urls'
    ALDRYN_BOILERPLATE_NAME = 'bootstrap4'
    ALDRYN_COMMON_PAGINATOR_PAGINATE_BY = ''
    ALDRYN_DJANGO_ENABLE_GIS = False
    ALDRYN_SITES_DOMAINS = {}
    ALDRYN_SITES_REDIRECT_PERMANENT = False
    ALLOWED_HOSTS = ['localhost', '*']
    SITE_ID = 1
    IS_RUNNING_DEVSERVER = False

USE_I18N = False

try:
    LANGUAGES
except:
    LANGUAGE_CODE = 'en'
    LANGUAGES = [('en', 'English')]

try:
    MEDIA_ROOT
except:
    MEDIA_ROOT = os.path.join(BASE_DIR, "/data/media")

EVALUATION_WINDOW = 4

THUMBNAIL_CACHE_DIMENSIONS = True
THUMBNAIL_HIGH_RESOLUTION = False
THUMBNAIL_OPTIMIZE_COMMAND = {}
THUMBNAIL_PRESERVE_EXTENSIONS = ['png', 'gif']
THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters')
THUMBNAIL_QUALITY = 90
THUMBNAIL_SOURCE_GENERATORS = ('easy_thumbnails.source_generators.pil_image',)

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'mail@burlesque-expo.com'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'gbe.auth.EmailUsernameAuth',
]
ADMINS = [('Admin',
           'admin@email.com'), ]
CMS_TEMPLATES = (
    ('base.html', 'base.html'),
)
