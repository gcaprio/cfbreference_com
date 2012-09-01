import os
import log

if os.environ.has_key('ENV') and os.environ['ENV'].lower() == "pro":
    from envs.pro_settings import *
else:
    from envs.local_settings import *

# Start Logging
log.init_logging(LOGGING_DIR)

TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)

# Django Default Date Format Override
DATE_FORMAT = 'N j, Y'

# Admins get notified of 500 errors
ADMINS = (
('admin', 'tech@cfbreference.com'),
)

# Managers get notified of 404 errors
MANAGERS = ADMINS

# Default email address 500 / 404 emails get sent from
SERVER_EMAIL = 'tech@cfbreference.com'

# Email admins when users hit a 404
SEND_BROKEN_LINK_EMAILS = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Root directory for local static file serving.
STATIC_DOC_ROOT = PROJECT_DIR + "/static/"

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www.cfbreference.com/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

ROOT_URLCONF = PROJECT_NAME + '.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates').replace('\\', '/'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django_extensions',
    'debug_toolbar',
    'common',
    'college',
    #'blog',
    'rankings',
    'scrapers',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'i(pit_g!zlkkf_^%@-io$bp6#&u#k^vu65)=n@-t)d%6ep&4ef'

CURRENT_SEASON = 2012

EMAIL_SUBJECT_PREFIX = '[College Football Reference] '