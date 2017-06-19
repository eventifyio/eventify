"""
Event Module
"""
import json
import logging
from datetime import datetime
from uuid import uuid4


logger = logging.getLogger('eventify.event')


class Event(object):
    """
    Event object
    """

    def __init__(self, event, **kwargs):
        """
        Create event
        :param event: Dictionary object
        :param kwargs: allow for customizing event
        """
        self.name = event.get('name')
        self.timestamp = event.get('timestamp', str(datetime.utcnow()))
        self.trace_id = event.get('trace_id', str(uuid4()))
        self.event_id = event.get('event_id', str(uuid4()))

        if event.get('message') is not None:
            try:
                if isinstance(event['message'], dict):
                    self.message = json.dumps(event['message'])
                else:
                    self.message = event['message']
            except ValueError:
                self.message = event['message']

        if kwargs is not None:
            for (key, value) in kwargs.items():
                setattr(self, key, value)

    def as_json(self):
        """
        Convert to dictionary
        """
        return self.__dict__


def default_var(value, default, stringify=False):
    """
    Set default variables
    :param value:
    :param default:
    :return: result
    """
    if value is None:
        if stringify:
            return str(value)
        return default
    return value
