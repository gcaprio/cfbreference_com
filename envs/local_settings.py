import os
from env_vars import *

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'cfbreference_com',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

SITE_ID = 3

CACHE_BACKEND="locmem:///"

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS' : False,
}

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(LOGGING_DIR, 'cfbreference_com.email.log').replace('\\', '/')