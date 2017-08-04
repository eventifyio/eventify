"""
Service Module
"""
from __future__ import print_function

import logging

from functools import wraps

from eventify.event import Event
from eventify.tracking import track_event
from eventify.tracking.constants import EventState
from eventify.drivers.crossbar import Service as CrossbarService


logger = logging.getLogger('eventify.service')


def event_tracker(func):
    """
    Event tracking handler
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        """
        Wraps function to provide redis
        tracking
        """
        event = Event(args[0])
        session = kwargs['session']
        service_name = session.name
        await track_event(event, EventState.started, service_name)
        await func(*args, **kwargs)
        await track_event(event, EventState.completed, service_name)
    return wrapper


class Service(CrossbarService):
    """
    Crossbar Service
    """
    pass
