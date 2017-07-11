#!/usr/bin/env python
"""
Minimal viable microservice
"""
import asyncio
import logging
import sys

from eventify.event import Event
from eventify.service import Service, event_tracker


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('example.consumer')


@event_tracker
async def my_example_event_handler(event, session=None):
    """
    Example event handler - This function is implemented as
    a callback method to the eventify service
    :param event: An event dictionary
    :param session: Access to the underlying methods of eventify
    """
    # Parse Incoming Event from Dict to Object
    event = Event(event)

    # See the event that was received
    logger.debug("received event %s", event.name)
    print('received event %s' % event.name)

    # Create and Publish an Event
    # you can also use the publish method directly
    new_event = Event({
        "name": "ReceivedEvent",
        "message": "Event received by consumer",
        "trace_id": event.trace_id
    })
    await session.emit_event(new_event)
    print("emitted event")


def run():
    logger.debug('service started')
    service = Service(
        config_file='config.json',
        callback=my_example_event_handler
    ).start()

if __name__ == '__main__':
    run()
