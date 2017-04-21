"""
User defined exceptions for
this service
"""

class ConfigError(Exception):
    """
    Exception raised when missing required configuration values
    """

    def __init__(self, message):
        self.message = message
