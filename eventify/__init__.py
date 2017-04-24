"""
Eventify!
A simple module for implementing event driven systems
"""
import json
import os

from eventify.exceptions import ConfigError


class Eventify(object):
    """
    Base Class for eventify
    """

    def __init__(self, driver='crossbar', config_file='config.json'):
        """
        Args:
            driver
        """
        self.driver = driver
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """
        Load configuration for the service
        """
        if os.path.exists(self.config_file):
            with open(self.config_file) as file_handle:
                config = file_handle.read()
                file_handle.close()
                return json.loads(config)

        raise ConfigError('Configuration is required! Missing: %s' % self.config_file)
