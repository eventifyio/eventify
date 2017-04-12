"""
Eventify!
A simple module for implementing event driven systems
"""
import logging


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

        if 'db_host' in kwargs:
            self.db_host = kwargs['db_host']
        if 'db_user' in kwargs:
            self.db_user = kwargs['db_user']
        if 'db_pass' in kwargs:
            self.db_pass = kwargs['db_pass']

    def get_version(self):
        """
        Returns current version of Eventify
        """
        return self.version
