"""
Eventify!
A simple module for implementing event driven systems
"""
import asyncio
import logging
import json
import os
from eventify.exceptions import EventifyConfigError, EventifyInitError

# Set uvloop as event loop for performance gains
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

logger = logging.getLogger('eventify')


class Eventify(object):
    """
    Base Class for eventify
    """

    def __init__(self, driver='crossbar', config_file='config.json', handlers=None):
        """
        Args:
            Driver
        """
        handlers = handlers or []
        logger.debug('initializing eventify project on driver: %s', driver)
        if not handlers:
            raise EventifyInitError("callback parameter is required")

        self.driver = driver
        self.config_file = config_file
        self.config = self.load_config
        self.handlers = handlers

        self.config_sanity_check()
        self.set_missing_defaults()

        logger.debug('configuration loaded: %s', self.config)

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

        if 'subscribed_topics' not in self.config:
            self.config['subscribed_topics'] = None

        if 'replay_events' not in self.config:
            self.config['replay_events'] = False

        if 'max_reconnect_retries' not in self.config:
            self.config['max_reconnect_retries'] = 10


    def config_sanity_check(self):
        """
        Base configuration sanity checks
        """
        if 'name' not in self.config:
            raise EventifyConfigError(
                'Required configuration parameter missing! Please configure "name" as a string in your configuration.')

        if 'publish_topic' not in self.config:
            raise EventifyConfigError(
                'Required configuration parameter missing! Please configure "public_topic" as an object in your configuration.')

        if 'topic' not in self.config['publish_topic']:
            raise EventifyConfigError(
                'Required configuration parameter missing! Please configure "topic" as a key in your "public_topic object.')


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
                return json.load(file_handle)
        else:
            logger.error('configuration file is required for eventify')
        logger.error('unable to load configuration for service')
        raise EventifyConfigError('Configuration is required! Missing: %s' % self.config_file)
