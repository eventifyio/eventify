"""
Eventify!
A simple module for implementing event driven systems
"""
import logging
import json
import os

from eventify.pubsub.publish import Publisher
from eventify.pubsub.subscribe import Subscriber

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)


class Eventify(object):
    """
    Base Class for eventify
    """

    def __init__(self, **kwargs):
        """
        Keyword Args:
            driver (basestring): Driver name
        """
        if 'config' in kwargs:
            config = kwargs['config']

            if os.path.exists(config):
                with open(config) as data_file:
                    service_configuration = json.load(data_file)
                    self.driver = service_configuration.get('driver', None)
                    self.topics_subscribed_to = service_configuration.get(
                        'topics_subscribed_to', None)
                    self.events_to_process = service_configuration.get(
                        'events_to_process', None)
                    self.transport_host = service_configuration.get(
                        'transport_host', None)

        if self.driver == 'crossbar':
            self.publisher = Publisher
            self.subscriber = Subscriber
