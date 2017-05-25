import logging
import json
import sys

from eventify.consumer import Consumer
from eventify.producer import Producer


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('example.consumer')

def handler(**kwargs):
    """
    Callback function to handle events as they arrive
    :param kwargs: Keyword args
    """
    # Parse event
    event_name = kwargs.get('name')
    event_body = json.loads(kwargs.get('message'))
    event_timestamp = kwargs.get('timestamp')
    event_trace_id = kwargs.get('trace_id')
    event_id = kwargs.get('event_id')

    # Just some logging
    logger.debug('event_id: {0}'.format(event_id))
    logger.debug('trace_id: {0}'.format(event_trace_id))
    logger.debug('timestamp: {0}'.format(event_timestamp))
    logger.debug('event_name: {0}'.format(event_name))
    logger.debug('message: {0}'.format(event_body))

    # Publish something

if __name__ == '__main__':
    """
    Start the consumer service
    """
    logger.debug('service started')

    consumer = Consumer(
        config_file='config.json', # Specify configuration
        callback=handler           # Define callback function
    )
    consumer.start()               # Start the event loop
