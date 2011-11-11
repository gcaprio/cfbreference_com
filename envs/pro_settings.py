import os
from env_vars import *

DEBUG = False

DATABASES = {
    'default': {
        'NAME': 'cfbreference_com',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'postgres',
        'PASSWORD': '3U1Tjq]$KJWXbnLuPDkC',
        'OPTIONS': {
            'autocommit': True,
        },
    }
}

SITE_ID = 2

CACHE_BACKEND="locmem:///"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "smtp@cfbreference.com"
EMAIL_HOST_PASSWORD = "rmYyTPoVQk1IDzAGM5lv"
EMAIL_USE_TLS = True

LOGGING_DIR = "/home/deploy/log/www.cfbreference.com/"