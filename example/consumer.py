"""
Minimal viable microservice
"""
import logging
import sys

from eventify.event import Event
from eventify.service import Service


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('example.consumer')

def my_example_event_handler(event, session=None):
    """
    Example event handler
    """
    # Parse Incoming Event
    event = Event(event)

    # Create and Publish an Event
    new_event = Event({
        "name": "ReceivedEvent",
        "message": "Event received by consumer",
        "trace_id": event.trace_id
    })

    session.emit_event(new_event)


def run():
    logger.debug('service started')
    service = Service(
        config_file='config.json',
        callback=my_example_event_handler
    ).start()

if __name__ == '__main__':
    run()
