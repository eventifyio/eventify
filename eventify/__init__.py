"""
Eventify!
A simple module for implementing event driven systems
"""
import logging
import json

import os

from eventify.exceptions import EventifyConfigError

logger = logging.getLogger('eventify')


class Eventify(object):
    """
    Base Class for eventify
    """

    def __init__(self, driver='crossbar', config_file='config.json', callback=None):
        """
        Args:
            Driver
        """
        logger.debug('initializing eventify project on driver: {0}'.format(driver))
        self.driver = driver
        self.config_file = config_file
        self.config = self.load_config
        logger.debug('configuration: {0}'.format(self.config))
        logger.debug('callback registered: {0}'.format(callback))
        self.callback = callback

    @property
    def load_config(self):
        """
        Load configuration for the service

        Args:
            config_file: Configuration file path
        """
        logger.debug('loading config file: {0}'.format(self.config_file))
        if os.path.exists(self.config_file):
            with open(self.config_file) as file_handle:
                config = file_handle.read()
                file_handle.close()
                logger.debug('configuration file successfully loaded')
                return json.loads(config)
        else:
            logger.error('configuration file is required for eventify')
        logger.error('unable to load configuration for service')
        raise EventifyConfigError('Configuration is required! Missing: %s' % self.config_file)
