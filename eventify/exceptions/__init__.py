"""
Eventify exceptions
"""

class ConfigError(Exception):
    """
    Configuration related errors
    """

    def __init__(self, message):
        self.message = message
        super(ConfigError, self).__init__(message)
