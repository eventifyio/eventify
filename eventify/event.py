"""
Event Module
"""
import json
import logging
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger('eventify.event')


class Event:
    """
    Event object
    """

    def __init__(self, name, message=None, timestamp=None, trace_id=None, **kwargs):
        """
        Create event
        :param name: event name
        :param message: event body
        :param kwargs: allow for customizing event
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        if trace_id is None:
            trace_id = uuid4()

        self.name = name
        self.timestamp = timestamp

        # Event Id - For Unique Event Identification
        self.event_id = uuid4()

        # Trace Id - For Tracking Flow Through a System
        self.trace_id = trace_id

        try:
            if isinstance(message, dict):
                self.message = json.dumps(message)
            else:
                self.message = message
        except ValueError:
            self.message = message

        if kwargs is not None:
            for (key, value) in kwargs.items():
                setattr(self, key, value)

        logger.debug('event object created: {0}'.format(self))
