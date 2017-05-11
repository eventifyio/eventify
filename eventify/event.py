"""
Event Module
"""
from datetime import datetime

import json
import re

class Event:
    """
    Event object
    """

    def __init__(self, name, message=None, timestamp=None, **kwargs):
        """
        Create event
        :param name: event name
        :param message: event body
        :param kwargs: allow for customizing event
        """
        if timestamp is None:
            timestamp = datetime.now()

        self.name = name
        self.timestamp = timestamp

        try:
            if isinstance(message, dict):
                self.message = json.dumps(message)
            else:
                self.message = message
        except ValueError as e:
            self.message = message

        if kwargs is not None:
            for (key, value) in kwargs.items():
                setattr(self, key, value)
