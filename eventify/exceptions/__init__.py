"""
Eventify exceptions
"""
import os
from raven import Client
from raven_aiohttp import AioHttpTransport


# Setup Sentry for Exception Tracking
SENTRY_DSN = os.getenv('SENTRY_DSN', None)
if SENTRY_DSN is not None:
    SENTRY_CLIENT = Client(SENTRY_DSN, transport=AioHttpTransport)
else:
    SENTRY_CLIENT = None

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


class EventifyPersistanceConfigError(Exception):
    """
    Errors with persistance configuration
    """

    def __init__(self, message):
        self.message = message
        super(EventifyPersistanceConfigError, self).__init__(message)


class EventifySanityError(Exception):
    """
    Errors with security and sanity
    """

    def __init__(self, message):
        self.message = message
        super(EventifySanityError, self).__init__(message)


class EventifyHandlerInitializationFailed(Exception):
    """
    Error initialization of handler. It means that we can not continue working so service should be stopped
     with non zero exit code
    """

    def __init__(self, message):
        self.message = message
        super(EventifyHandlerInitializationFailed, self).__init__(message)
