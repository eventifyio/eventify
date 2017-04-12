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
        :param driver: Driver you wish to use
        :param kwargs: Driver settings
        """
        self.version = '0.1.5'


    @tornado.gen.coroutine
    def load_config(self):
        """
        Load config onto stream instance
        """
        logger.debug("configuration file specified: %s" % self.config)
        if os.path.exists(self.config):
            logger.debug("configuration file exists!")
            with open(self.config) as data_file:
                self.service_configuration = json.load(data_file)
                logger.debug(self.service_configuration)


    @tornado.gen.coroutine
    def get_version(self):
        """
        Returns current version of Eventify
        """
        yield self.version
