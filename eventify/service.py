"""
Service Module
"""
from __future__ import print_function

import logging

from functools import wraps

from eventify import Eventify
from eventify.exceptions import EventifyConfigError


logger = logging.getLogger('eventify.service')


def driver_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            function_name = func.__name__
            driver_to_load = 'eventify.drivers.' + args[0].driver
            logger.debug('loading driver %s', driver_to_load)
            driver = __import__(driver_to_load, globals(), locals(), ['create_service'])
            service = driver.create_service()
            call_method = getattr(service, function_name)(args[0])
        except KeyError as error:
            logger.error(error)
    return wrapper


class Service(Eventify):
    """
    Abstract service creation to support use of multiple drivers
    in the future
    """

    @driver_function
    def start(self):
        pass

    @driver_function
    def start_producer(self):
        pass
