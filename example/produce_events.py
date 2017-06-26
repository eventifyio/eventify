#!/usr/bin/env python
"""
Minimal viable microservice that publishes events
to test how system works
"""
import logging
import sys

from eventify.event import Event
from eventify.service import Service


FORMAT = '%(asctime)-15s %(name)s %(levelname)s %(message)s'
logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger('event.producer')

def produce_events(session):
    """
    Produces 10 events
    """
    for number in range(1,11):
        event = Event({
            "name": "EventProduced",
            "message": "Event %s" % number
        })
        session.emit_event(event)



if __name__ == '__main__':
    service = Service(config_file='config-producer.json', callback=produce_events)
    service.start_producer()
