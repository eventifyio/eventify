"""
Eventify!
A simple module for implementing event driven systems
"""
from __future__ import print_function

import logging
import os
import sys
import time


class Eventify(object):
    """
    Base Class for eventify
    """
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)


    def __init__(self, driver, **kwargs):
        """
        :param driver: Driver you wish to use
        :param kwargs: Driver settings
        """
        if driver == 'producer':
            self.init_producer()
        elif driver == 'consumer':
            self.init_consumer()
        else:
            raise ValueError("Driver not supported: %s" % self.driver)
