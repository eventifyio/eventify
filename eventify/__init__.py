"""
Eventify!
A simple module for implementing event driven systems
"""
import logging


class Eventify(object):
    """
    Base Class for eventify
    """
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)


    def __init__(self, **kwargs):
        """
        :param driver: Driver you wish to use
        :param kwargs: Driver settings
        """
        self.version = '0.1.1'

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
