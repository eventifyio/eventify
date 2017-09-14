"""
Eventify Persistance Configuration
"""
import os

EVENT_DB_HOST = os.getenv('EVENT_DB_HOST', None)
EVENT_DB_USER = os.getenv('EVENT_DB_USER', None)
EVENT_DB_PASS = os.getenv('EVENT_DB_PASS', None)
EVENT_DB_NAME = os.getenv('EVENT_DB_NAME', 'event_history')
