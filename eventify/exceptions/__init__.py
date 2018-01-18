"""
Eventify exceptions
"""


class EventifyError(Exception):
    """
    Configuration related errors
    """

    def __init__(self, message):
        self.message = message
        super(EventifyError, self).__init__(message)


class EventifyConfigError(EventifyError):
    """
    Configuration related errors
    """

    def __init__(self, message):
        self.message = message
        super(EventifyConfigError, self).__init__(message)


class EventifyInitError(EventifyError):
    """
    Initialization errors
    """

    def __init__(self, message):
        self.message = message
        super(EventifyInitError, self).__init__(message)


class EventifyPersistanceConfigError(EventifyError):
    """
    Errors with persistance configuration
    """

    def __init__(self, message):
        self.message = message
        super(EventifyPersistanceConfigError, self).__init__(message)


class EventifySanityError(EventifyError):
    """
    Errors with security and sanity
    """

    def __init__(self, message):
        self.message = message
        super(EventifySanityError, self).__init__(message)


class EventifyHandlerInitializationFailed(EventifyError):
    """
    Error initialization of handler. It means that we can not continue working so service should be stopped
     with non zero exit code
    """

    def __init__(self, message):
        self.message = message
        super(EventifyHandlerInitializationFailed, self).__init__(message)
