"""
Eventify!
A simple module for implementing event driven systems
"""
import logging
import json
import os

import tornado.gen

# Setup logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)


class Eventify(object):
    """
    Base Class for eventify
    """


    def __init__(self, **kwargs):
        """
        Args:
            driver (basestring): Driver name
        """
        self.version = '0.1.5'


    @tornado.gen.coroutine
    def load_config(self):
        """
        Load config onto stream instance
        """
        if os.path.exists(self.config):
            with open(self.config) as data_file:
                service_configuration = json.load(data_file)
                driver = service_configuration.get('driver', None)
                topics_subscribed_to = service_configuration.get('topics_subscribed_to', None)
                events_to_process = service_configuration.get('events_to_process', None)
                topics_publishing_to = service_configuration.get('topics_publishing_to', None)
                queue_host = service_configuration.get('queue_host', None)
                if driver is not None:
                    self.driver = driver
                if topics_subscribed_to is not None:
                    self.topics_subscribed_to = topics_subscribed_to
                if events_to_process is not None:
                    self.events_to_process = events_to_process
                if topics_publishing_to is not None:
                    self.topics_publishing_to = topics_publishing_to
                if queue_host is not None:
                    self.host = queue_host


    def set_topic(self, topic):
        """
        Set topic for instance of Stream

        Args:
            topic (basestring): Name of topic
        """
        self.topic = topic


    def set_host(self, host):
        """
        Set host for topic for instance of Stream

        Args:
            host (basestring): FQDN of queue server
        """
        self.host = host


    @tornado.gen.coroutine
    def get_version(self):
        """
        Returns current version of Eventify
        """
        yield self.version
