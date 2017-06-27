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
    """
    Decorator for proxying calls to drivers

    Granted this is a little hacky it solves the problem where the
    eventify project is not locked into a specific technology or
    provider and allows for us to transparently change underlying
    tech stack as necessary
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Get the function we want to execute on the driver
            function_name = func.__name__

            # Import driver dynamically
            driver_to_load = 'eventify.drivers.' + args[0].driver
            logger.debug('loading driver %s', driver_to_load)
            driver = __import__(driver_to_load, globals(), locals(), ['create_service'])

            # Create service on driver
            service = driver.create_service()

            # Execute original function
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
    def start(self): pass

    @driver_function
    def start_producer(self): pass
