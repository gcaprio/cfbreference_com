# Template WSGI file for Apache / WSGI.
import site
import os
import sys

#include virtualenv libs
site.addsitedir('/home/deploy/.virtualenvs/www.cfbreference.com/lib/python2.6/site-packages')

sys.path.append('/home/deploy/www/www.cfbreference.com')
sys.path.append('/home/deploy/www/www.cfbreference.com/cfbreference_com')

# Set correct settings variable.
os.environ['DJANGO_SETTINGS_MODULE'] = 'cfbreference_com.settings'

import django.core.handlers.wsgi

# Set target environment variable to load correct settings.py file.
os.environ['ENV'] = 'pro'

# Lastly, load handler.
application = django.core.handlers.wsgi.WSGIHandler()
