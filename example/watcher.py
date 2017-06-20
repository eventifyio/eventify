"""
Minimal viable microservice
"""
import logging
import sys

from eventify.service import Service


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('example.consumer')

def my_example_event_handler(*args, publish=None, **kwargs):
    """
    Example event handler
    """
    logger.debug(kwargs)

def run():
    logger.debug('service started')
    service = Service(
        config_file='config-debug.json',
        callback=my_example_event_handler
    ).start()

if __name__ == '__main__':
    run()
