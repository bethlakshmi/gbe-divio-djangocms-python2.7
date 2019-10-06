import os

"""
Django settings for expo project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

"""


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
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'aldryn_django',
    'aldryn_sites',
    'cms',
    'aldryn_django_cms',
    'menus',
    'sekizai',
    'treebeard',
    'parler',
    'aldryn_boilerplates',
    'django.contrib.sitemaps',
    'compressor',
    'robots',
    'captcha',
    'django_select2',
    u'filer.contrib.django_cms',
    u'aldryn_common',
    u'djangocms_icon',
    u'djangocms_link',
    u'djangocms_picture',
    u'djangocms_bootstrap4',
    u'djangocms_bootstrap4.contrib.bootstrap4_alerts',
    u'djangocms_bootstrap4.contrib.bootstrap4_badge',
    u'djangocms_bootstrap4.contrib.bootstrap4_card',
    u'djangocms_bootstrap4.contrib.bootstrap4_carousel',
    u'djangocms_bootstrap4.contrib.bootstrap4_collapse',
    u'djangocms_bootstrap4.contrib.bootstrap4_content',
    u'djangocms_bootstrap4.contrib.bootstrap4_grid',
    u'djangocms_bootstrap4.contrib.bootstrap4_jumbotron',
    u'djangocms_bootstrap4.contrib.bootstrap4_link',
    u'djangocms_bootstrap4.contrib.bootstrap4_listgroup',
    u'djangocms_bootstrap4.contrib.bootstrap4_media',
    u'djangocms_bootstrap4.contrib.bootstrap4_picture',
    u'djangocms_bootstrap4.contrib.bootstrap4_tabs',
    u'djangocms_bootstrap4.contrib.bootstrap4_utilities',
    u'djangocms_file', u'djangocms_googlemap',
    u'djangocms_history', u'djangocms_snippet',
    u'djangocms_style', u'djangocms_text_ckeditor',
    u'djangocms_video',
    u'filer',
    u'easy_thumbnails',
    u'mptt',
    u'polymorphic',
    'tinymce',
    'scheduler',
    'ticketing',
    'gbe',
    'post_office',
    'import_export',
    'snowpenguin.django.recaptcha2']

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

DEBUG = True

try:
    SECRET_KEY
except:
    SECRET_KEY = '0sdq74686*ayl^0!tqlt*!mgsycr)h4h#*4*_x=2_dw9cq8d!i'

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
                'aldryn_boilerplates.context_processors.boilerplate',
                'aldryn_snake.template_api.template_processor'],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'aldryn_boilerplates.template_loaders.AppDirectoriesLoader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader']},
        'BACKEND': 'django.template.backends.django.DjangoTemplates'}]

'''
MIDDLEWARE_CLASSES = [
    'cms.middleware.utils.ApphookReloadMiddleware', #
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', #
    'django.middleware.csrf.CsrfViewMiddleware', #
    'django.contrib.auth.middleware.AuthenticationMiddleware', #
    'django.contrib.messages.middleware.MessageMiddleware', #
    'aldryn_django.middleware.LanguagePrefixFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware', #
    'django.contrib.sites.middleware.CurrentSiteMiddleware', #
    'aldryn_sites.middleware.SiteMiddleware', #
    'django.middleware.security.SecurityMiddleware', #
    'django.middleware.common.CommonMiddleware', #
    'django.middleware.clickjacking.XFrameOptionsMiddleware', #
    'cms.middleware.user.CurrentUserMiddleware', #
    'cms.middleware.page.CurrentPageMiddleware', #
    'cms.middleware.toolbar.ToolbarMiddleware', #
    'cms.middleware.language.LanguageCookieMiddleware']
'''
MIDDLEWARE_CLASSES = (
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'aldryn_sites.middleware.SiteMiddleware',
    'django.middleware.common.CommonMiddleware',
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
    ALDRYN_BOILERPLATE_NAME = u'bootstrap4'
    ALDRYN_COMMON_PAGINATOR_PAGINATE_BY = u''
    ALDRYN_DJANGO_ENABLE_GIS = False
    ALDRYN_SITES_DOMAINS = {}
    ALDRYN_SITES_REDIRECT_PERMANENT = False
    ALLOWED_HOSTS = ['localhost', '*']
    SITE_ID = 1
    IS_RUNNING_DEVSERVER = False

try:
    LANGUAGES
except:
    LANGUAGE_CODE = u'en'
    LANGUAGES = [(u'en', u'English')]

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

RECAPTCHA_PRIVATE_KEY = '6Le0dx0UAAAAACNZynxCx5mUovu3M1Au3XFeeFKN'
RECAPTCHA_PUBLIC_KEY = '6Le0dx0UAAAAAFGd_HJzX22FdzhwI-GCh8nCoXoU'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'mail@burlesque-expo.com'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'gbe.auth.EmailUsernameAuth',
]
