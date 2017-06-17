"""
Eventify exceptions
"""

class EventifyConfigError(Exception):
    """
    Configuration related errors
    """

    def __init__(self, message):
        self.message = message
        super(EventifyConfigError, self).__init__(message)

class EventifyInitError(Exception):
    """
    Initialization errors
    """

    def __init__(self, message):
        self.message = message
        super(EventifyInitError, self).__init__(message)
