"""
Eventify Tracking Constants
"""
import os


EVENT_TRACKING_HOST = os.getenv('EVENT_TRACKING_HOST', 'localhost')


class EventState(object):
    """
    Event States
    """
    started = 'STARTED'
    inflight = 'IN-FLIGHT'
    completed = 'COMPLETED'
