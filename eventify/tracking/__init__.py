"""
Event Tracking Module
"""
from datetime import datetime

import logging
import redis

from eventify.tracking.constants import EVENT_TRACKING_HOST


logger = logging.getLogger('eventify.tracking')
r = redis.StrictRedis(host=EVENT_TRACKING_HOST, port=6379, db=0)


def track_event(event, state, service_name):
    """
    Store state of events in memory
    :param event: Event object
    :param state: EventState object
    :param service_name: Name of service name
    """
    now = datetime.utcnow()
    event_id = event.event_id
    logger.debug("tracking event %s with state %s", event_id, state)

    tracking_data = {
        "event_id": event_id,
        "timestamp": str(now),
        "state": state
    }

    # Check if key already exists
    try:
        exists = r.exists(service_name)
        if exists:
            # Add next state to redis key
            r.rpush(service_name, tracking_data)
        else:
            # Create new redis key
            r.rpush(service_name, tracking_data)
    except redis.exceptions.ConnectionError as error:
        logger.error(error)
        logger.warning('Having a REDIS instance is the recommended method of running eventify')


def get_last_event(service_name):
    """
    Get the last event on cache
    :param service_name: Name of service
    """
    print(r.rpop(service_name))
