"""
Eventify!
A simple module for implementing event driven systems
"""
import logging
import json
import os

from eventify.exceptions import EventifyConfigError, EventifyInitError


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
        logger.debug('initializing eventify project on driver: %s', driver)
        if callback is None:
            raise EventifyInitError("callback parameter is required")

        self.driver = driver
        self.config_file = config_file
        self.config = self.load_config
        self.callback = callback
        self.set_missing_defaults()
        logger.debug('configuration: %s', self.config)

    def set_missing_defaults(self):
        """
        Ensure that minimal configuration is
        setup and set defaults for missing values
        """
        if 'pub_options' not in self.config:
            self.config['pub_options'] = {
                'acknowledge': True,
                'retain': True
            }

        if 'sub_options' not in self.config:
            self.config['sub_options'] = {
                'get_retained': False
            }

        if 'replay_events' not in self.config:
            self.config['replay_events'] = False

        if 'subscribed_topics' not in self.config:
            raise EventifyConfigError('Required configuration parameter missing! Please configure "subscribed_topics" as an array in your configuration.')

        if 'publish_topic' not in self.config:
            raise EventifyConfigError('Required configuration parameter missing! Please configure "public_topic" as an object in your configuration.')

        if 'topic' not in self.config['publish_topic']:
            raise EventifyConfigError('Required configuration parameter missing! Please configure "topic" as a key in your "public_topic object.')


    @property
    def load_config(self):
        """
        Load configuration for the service

        Args:
            config_file: Configuration file path
        """
        logger.debug('loading config file: %s', self.config_file)
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
