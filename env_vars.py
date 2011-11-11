"""
Holds common environment specific variables
"""
import os
import django

# Current Project Directory
PROJECT_DIR = os.path.realpath(os.path.dirname(__file__))
# Current Project Name
PROJECT_NAME = os.path.split(PROJECT_DIR)[1]
# Root Directory for Django
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
# Logging Directory
try:
    LOGGING_DIR
except:
    LOGGING_DIR = PROJECT_DIR
