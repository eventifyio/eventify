#!/usr/bin/env python
"""
Minimal viable microservice that publishes events
to test how system works
"""
import asyncio
import logging
import sys
import time

from eventify.event import Event
from eventify.service import Service


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('event.producer')

def produce_events(session):
    """
    Produces 10 events
    """
    print('called')
    logger.debug('called')
    counter = 1
    for number in range(1,11):
        print(counter)
        logger.debug("setting up event")
        event = Event({
            "name": "EventProduced",
            "message": "Event %s" % number
        })
        logger.debug("event setup")
        session.emit_event(event)
        counter = counter + 1
        time.sleep(1)


if __name__ == '__main__':
    service = Service(config_file='config-producer.json', callback=produce_events)
    service.start_producer()
