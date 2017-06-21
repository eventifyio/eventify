"""
Minimal viable microservice
"""
import logging
import sys

from eventify.event import Event
from eventify.service import Service


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('watcher.consumer')


def my_example_event_handler(event, session=None):
    """
    Example event handler
    """
    # Load Event
    event = Event(event)
    logger.debug("handling event: %s", event.name)


def run():
    logger.debug('service started')
    service = Service(
        config_file='config-debug.json',
        callback=my_example_event_handler
    ).start()

if __name__ == '__main__':
    run()
