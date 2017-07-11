"""
Eventify Persistance Configuration
"""
import os

from eventify.exceptions import EventifyPersistanceConfigError


EVENT_DB_HOST = os.getenv('EVENT_DB_HOST', None)
EVENT_DB_USER = os.getenv('EVENT_DB_USER', None)
EVENT_DB_PASS = os.getenv('EVENT_DB_PASS', None)
EVENT_DB_NAME = os.getenv('EVENT_DB_NAME', 'event_history')

if EVENT_DB_HOST is None:
    raise EventifyPersistanceConfigError("In order to use database persistance you must configure 'EVENT_DB_HOST' as an environment variable")
if EVENT_DB_USER is None:
    raise EventifyPersistanceConfigError("In order to use database persistance you must configure 'EVENT_DB_USER' as an environment variable")
if EVENT_DB_PASS is None:
    raise EventifyPersistanceConfigError("In order to use database persistance you must configure 'EVENT_DB_PASS' as an environment variable")
